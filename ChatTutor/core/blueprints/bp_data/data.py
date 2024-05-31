# import pymysql
## search for TODO : modify
import io
import json
from typing import List

import PyPDF2
import flask
import os

import pdfreader

# import markdown
import flask_login
import requests

from core.blueprints.bp_data.paper_manager import PaperManager
from core.extensions import db
from flask import Blueprint, Response, jsonify, request
from datetime import datetime
from core.data import (
    DataBase,
    UserModel,
    MessageModel,
    FeedbackModel,
    SectionModel,
    CourseModel,
    ChatModel,
)
from scholarly import scholarly, Author, Publication
from google_scholar_py import *
from core.reader import parse_pdf, Text, Doc
from core.blueprints.bp_data.cqn import CQNPublications, process, load_citations
from serpapi import GoogleScholarSearch

from flask_apscheduler import APScheduler
from core.extensions import sched

data_bp = Blueprint("bp_data", __name__)


def format_entry(entry):
    return CQNPublications(entry).toDict()


@data_bp.route("/get_author_likeness", methods=["POST", "GET"])
def get_author_likeness():
    data = request.json
    if data is None:
        return jsonify({"no": "no json received"})

    name = data.get('name', '')

    print(f'got name: {name}')

    res, _ = DataBase().get_author_by_name_like(name_like=name)
    if res is None:
        return jsonify({"data": "no authoirs found!"})
    return jsonify({"data": res})

@data_bp.route("/add_from_json_to_db", methods=["GET"])
def add_from_json_to_db():
    dt = []
    with open("core/data/parsing/papers/papers_from_pdf.json", "r") as f:
        data = json.load(f)
        ff = []
        for x in data["data"]:
            x["resources"] = [{"link": PaperManager.convert_paper_link_to_resource_link(x.get('link', ''))}]
            if(x.get('link', '') == ''):
                x['link'] = ''
            ff.append(x)
            print("::TT::", x)
        dt = [JSONPaperParser().parse(x) for x in ff]
    print("\n\n\naaaaaaaaaaaa\n\n\n")
    PaperManager.add_to_database_pdfs(dt=dt)
    print("Added!")
    PaperManager.add_to_chroma_static(dt=dt)
    return jsonify({"data": [x for x in dt]})


@data_bp.route("/get_complete_papers", methods=["POST", "GET"])
def get_complete_papers():
    res, _ = DataBase().get_complete_papers_by_author()
    return jsonify({"data": res})


@data_bp.route("/get_paper_by", methods=["POST"])
def get_paper_by():
    result = request.json
    a_id = result.get("author_id", None)
    a_name = result.get("author_name", None)
    res, _ = DataBase().get_papers_written_by(author_id=a_id, author_name=a_name)

    return jsonify({"data": res})


@data_bp.route("/get_authors", methods=["GET", "POST"])
def get_authors():
    res, _ = DataBase().get_all_authors()
    return jsonify({"data": res})


@data_bp.route("/get_authors_by_name", methods=["GET", "POST"])
def get_authors_by_name():
    result = request.json
    a_name = result.get("author_name", None)
    res, _ = DataBase().get_author_by_name(a_name)
    return jsonify({"data": res})


@data_bp.route("/get_papers_by_name", methods=["GET", "POST"])
def get_papers_by_name():
    result = request.json
    a_name = result.get("paper_name", None)
    res, _ = DataBase().get_paper_by_name(a_name)
    res2, _ = DataBase().search_publications(a_name)
    return jsonify({"data": res + res2})


@data_bp.route("/get_papers_by_query", methods=["GET", "POST"])
def get_papers_by_query():
    print("aaaaaaa\n")
    result = request.json
    a_name = result.get("paper_query", None)
    res, _ = DataBase().search_publications(a_name)

    print("\n\n-----------\n")
    print(res)
    print("\n-----------\n\n")

    return jsonify({"data": res})


@data_bp.route("/get_authors_for_papers", methods=["POST"])
def get_authors_for_papers():
    result = request.json
    a_id = result.get("paper_id", None)
    res, _ = DataBase().get_authors_of_paper(paper_id=a_id)
    return jsonify({"data": res})


@data_bp.route("/getchromapapers", methods=["POST"])
def getchromapapers():
    # print("sgdfksdafgdbs")
    req_js = request.json
    prompt = req_js.get("prompt", None)
    variant = req_js.get("variant", None)
    db.load_datasource_papers("cqn_ttv")
    docs, met, dist, text, ceva = db.query_papers_m(
        prompt=prompt, n_results=10, from_doc=None, variant=variant, metadatas=True
    )
    ids = ceva["ids"]
    docs = ceva["documents"]

    flat_ids = []
    for id_l in ids:
        for id in id_l:
            flat_ids.append(id)

    flat_docs = []
    for doc_l in docs:
        for doc in doc_l:
            flat_docs.append(doc)

    flat_met = []
    print(f"MET: {met}")
    for metl in met:
        flat_met.append(metl)

    flat_ = []
    for i in range(0, len(flat_docs)):
        flat_.append({"id": flat_ids[i], "document": flat_docs[i], "metadata": flat_met[i]})
        print(f"[-] i: {i} | met[i]: {flat_met[i]}")

    # TODO ANDU: ai result_idurile in flat_[i]["metadata"]["doc"]
    # intoarce aici pt fiecare si entriul din sql cu autori citatii etc
    print("\n\nbbbbbbbbbbbbbbb\n\n")
    all_db, _ = DataBase().get_complete_papers_by_author()
    print("\nbakekekek\n\n")

    print("\n\n\n")
    print(all_db.keys())
    all_all = []

    for docu in flat_:
        sql_id = docu["metadata"]["doc"]
        docu["metadata"]["info"] = all_db[sql_id]
        all_all.append(docu)

    print(f"\n\n\n\t[FLAT_] {all_all}")
    return jsonify(all_all)


from core.data.parsing.papers.json_papers import JSONPaperParser


@data_bp.route("/proba_cqn", methods=['POST', 'GET'])
def proba_cqn():
    #return jsonify({"andu": "andu"})
    alfa = refreshcqn_scheduler()
    if alfa is None:
        return jsonify({"maessaje": "err"})
    return jsonify({"data": alfa})



@data_bp.route("/backuploadcqn", methods=["POST", "GET"])
def backuploadcqn():
    # string = json.dumps(data, indent=2)

    # for i in range(0, len(data_filtered) - 1):
    #     data_filtered[i].set_pdf_contents(content_url=data_filtered[i].get_first_file_link())
    dt = []
    with open("core/blueprints/bp_data/data_backup.json", "r") as f:
        data = json.load(f)
        dt = [JSONPaperParser().parse(x) for x in data["data"]]
    print("\n\n\naaaaaaaaaaaa\n\n\n")
    PaperManager.add_to_database_static(dt=dt)
    print("Added!")
    # PaperManager.add_to_chroma(dt=dt)
    return jsonify({"data": [x for x in dt]})


#@data_bp.route("/refreshcqn", methods=["POST", "GET"])
#def refreshcqn():
 #   ps = SerpApiGoogleScholarOrganic()
  #  data = ps.scrape_google_scholar_organic_results(
 #       query="NSF-ERC CQN 1941583",
 #       api_key=os.getenv("SERP_API_KEY"),
 #       pagination=True,
 #   )

  #  data_formated: List[CQNPublications] = [CQNPublications(e) for e in data]

  #  data_filtered: List[CQNPublications] = list(
  #      filter(lambda x: x.resources != "None", data_formated)
  #  )
    # string = json.dumps(data, indent=2)

    # for i in range(0, len(data_filtered) - 1):
    #     data_filtered[i].set_pdf_contents(content_url=data_filtered[i].get_first_file_link())
   # get_content = True
  #  dt = data_filtered
  #  if get_content:
  #      dt = process(data_filtered)

  #  print("----- DONE -----")
  #  dt = [x for x in data_filtered if x is not None]

  #  with open("./data.json", "w+") as f:
  #      f.write(f"{dt}")

  #  PaperManager.add_to_database(dt=dt)
  #  print("Added!")
   # PaperManager.add_to_chroma(dt=dt)
   # return jsonify({"data": [x.toDict() for x in dt]})

def test_refresh():
    print('Hello world!')

def refreshcqn_scheduler():
    
    ps = SerpApiGoogleScholarOrganic()
    key = os.getenv("SERP_API_KEY")
    if key is None:
        return

    data = ps.scrape_google_scholar_organic_results(
            query="NSF-ERC CQN 1941583",
            api_key=key,
            pagination=True,
        )
    # ---- FROM BACKUP . JSON, DECOMMENT IN CASE OF ERR (doamne fereste) ----
    #dt = []
    #with open("core/blueprints/bp_data/data_backup.json", "r") as f:
    #    data = json.load(f)
    #    dt = [JSONPaperParser().parse(x) for x in data["data"]]

    
    dt = [JSONPaperParser().parse(x) for x in data]
    print("\n\n\naaaaaaaaaaaa\n\n\n")
    PaperManager.add_to_database_static(dt=dt)
    
    PaperManager.add_to_chroma_static(dt=dt)
    return {"data": "success"}

def getpdfcontentsfromlist(pubs: List[CQNPublications]):
    for i in range(0, len(pubs) - 1):
        f_link = pubs[i].get_first_file_link()
        pubs[i].set_pdf_contents(content_url=f_link, i=i)


@data_bp.route("/refreshcqnunformatted", methods=["POST", "GET"])
def refresh_unformatted():
    ps = SerpApiGoogleScholarOrganic()
    data = ps.scrape_google_scholar_organic_results(
        query="NSF-ERC CQN 1941583",
        api_key=os.getenv("SERP_API_KEY"),
        pagination=True,
    )
    # string = json.dumps(data, indent=2)
    return jsonify(data)


@data_bp.route("/addtodb", methods=["POST", "GET"])
def addtodb():
    """
        The `addtodb` function inserts a message into a database with the provided content, role, chat ID,
        clear number, and time created.
    3
        URLParams:
            ```
            {
                "content" : str, # content of the message
                "role" : str  "User" | "Assistant",
                "chat_k" : Optional[str],
                "clear_number" : int, # number of times the chat was cleared
                "time_created" : int,
                "credential_token" : Oprional[str], # unused for now
                "course" : Optional[str], # course which the message should be linked to
            }
            ```
        Returns:
            ```
            {
                "message_id" : str # inserted message db id
                ... + all provided info
            }
            ```
    """
    data = request.json
    course_col = data.get("course", None)  # HERE
    message_id = data.get("message_id", None)
    user_id = data.get("user_id", "LOGGED_OFF")
    content = data["content"]
    role = data["role"]
    chat_k_id = data.get("chat_k", "none")
    clear_number = data.get("clear_number", 0)
    time_created = data["time_created"]
    time_created = datetime.utcfromtimestamp(int(time_created) / 1000)
    credential_token = data.get("credential_token", "Not a valid token")
    # messageDatabase.insert_chat(chat_k_id)
    chat_id, _ = DataBase().insert_chat("none")
    print("> CHATKEY")
    print(chat_id)
    message_to_upload = {
        "message_id": message_id,
        "content": content,
        "role": role,
        "chat": chat_id,
        "clear_number": clear_number,
        "time_created": time_created,
        "credential_token": credential_token,
        "user_id": user_id,
    }

    print("adding ", message_to_upload, " to db")
    uploaded_message, _, user = DataBase().insert_message(
        message_to_upload, course_col, user_id
    )  # HERE
    print("succesfully added message ", "with users", user)
    return jsonify(
        {
            "message_id": uploaded_message.mes_id,
            "content": content,
            "role": role,
            "chat": chat_k_id,
            "clear_number": clear_number,
            "time_created": time_created,
            "credential_token": credential_token,
            "users": user,
        }
    )


@data_bp.route("/addmessagefeedback", methods=["POST", "GET"])
def addmessagefeedback():
    """Adds message feedback:
    URLParams:
        ```
        {
            "message_id" : str, # message id of the liked/unliked message
            "content" : str "Positive" | "Negative", #  feedback content : positive/negative
        }
        ```

    Returns:
        ```
        {
            "message_id": str, # same message id,
            "feedback_id": str, # inserted feedback id,
            "feedback_content": str "Positive" | "Negative", # same feedback content
        }
        ```
    """
    data = request.json
    message_id = data.get("message_id")
    if message_id is None:
        return jsonify({"message": "error"}), 404
    feedback_content = data.get("content")
    print("\n>> FEEDBACK")
    print(feedback_content)
    print(message_id)

    feedback_id, _ = DataBase().insert_feedback(
        FeedbackModel(content=feedback_content, message_id=message_id)
    )
    print("<< FEEDBACK\n")
    return (
        jsonify(
            {
                "message_id": message_id,
                "feedback_id": feedback_id,
                "feedback_content": feedback_content,
            }
        ),
        200,
    )


# TODO : remove this
# @data_bp.route("/delete_uploaded_data", methods=["POST"])
# def delete_uploaded_data():
#     """
#     The function `delete_uploaded_data` deletes a data source with a given collection name from a
#     database.
#     :return: a JSON response with the key "deleted" and the value being the name of the collection that
#     was deleted.
#     """
#     data = request.json
#     collection_name = data["collection"]
#     db.delete_datasource_chroma(collection_name)
#     return jsonify({"deleted": collection_name})


@data_bp.route("/delete_doc", methods=["POST"])
@flask_login.login_required
def delete_doc():
    """
    The `delete_doc` function deletes a document from a specified collection in a database.
    URLParams:
        ```
        {
            "collection" : str, # specified chroma collection name
            "doc" : str # document to remove
        }
        ```
    Returns:
        - a JSON response containing the name of the deleted document and the name of the collection
    it was deleted from.
        ```
        {"deleted": deleted doc, "from_collection": collection}
        ```
    """
    data = request.json
    collection_name = data["collection"]
    doc_name = data["doc"]
    if DataBase().validate_course_owner(
        collectionname=collection_name, user_email=flask_login.current_user.email
    ):
        collection = db.client.get_collection(name=collection_name)
        print(collection)
        collection.delete(where={"from_doc": doc_name})
        print("deleted")
        return jsonify({"deleted": doc_name, "from_collection": collection_name})
    return jsonify({"error": "Unauthorized operation."})


@data_bp.route("/add_doc_tosection", methods=["POST"])
@flask_login.login_required
def add_fromdoc_tosection():
    """
    The function `add_fromdoc_tosection` adds a URL to a specific section in a collection and returns a
    JSON response indicating the URL that was added and the collection it was added to.
    URLParams:
        ```
        {
            "collection" : str, # specified chroma collection name
            "section_id" : str, # section id to add url/file to
            "url_to_add" : str # url that will be added to the section knowledge base
            # for now only urls are supported in this operation
        }
        ```
    TODO: add another param : "file_to_add" form/multipart that would add files
    to the knowledge base.

    Returns:
    - a JSON response containing the URL that was added and the name of the collection it was
    added to.
        ```
        {
            "added": str, # url_to_add received from body
            "to_collection": str # collection name received from body
        }
        ```
    """
    data = request.json
    collection_name = data["collection"]
    section_id = data["section_id"]
    url_to_add = data["url_to_add"]
    if DataBase().validate_course_owner(
        collectionname=collection_name, user_email=flask_login.current_user.email
    ):
        DataBase().update_section_add_fromdoc(section_id=section_id, from_doc=url_to_add)
        return jsonify({"added": url_to_add, "to_collection": collection_name})
    return jsonify({"error": "Unauthorized operation."})


@data_bp.route("/get_section", methods=["POST"])
@flask_login.login_required
def get_section():
    """
    The function `get_section` retrieves a specific section from a collection and returns the section
    details along with the pulling_from (knowledge base urls) information.

    URLParams:
        ```
        {
            "collection" : str # collection name
            "section_id" : str # section id
        }
        ```
    Returns:
    - a JSON object that contains the sections and the pulling_from values.

        ```
        {
            "sections": list[Section] # sections (at least one),
            "pulling_from": list[str] # knowledge base of each section
        }
        ```
    """
    data = request.json
    collection_name = data["collection"]
    section_id = data["section_id"]
    if DataBase().validate_course_owner(
        collectionname=collection_name, user_email=flask_login.current_user.email
    ):
        sections, _ = DataBase().get_sections_by_id(section_id=section_id)
        pfrom = [s.pulling_from for s in sections]
        return jsonify({"sections": sections, "pulling_from": pfrom})
    return jsonify({"error", "Unauthorized operation"})
