# import pymysql
## search for TODO : modify
import flask
import os
# import markdown
import flask_login
from core.extensions import (db)
from flask import (Blueprint, Response, jsonify, request)
from datetime import datetime
from core.data import (
    DataBase,
    UserModel,
    MessageModel,
    FeedbackModel,
    SectionModel,
    CourseModel,
    ChatModel
)

data_bp = Blueprint("bp_data", __name__)


@data_bp.route("/addtodb", methods=["POST", "GET"])
def addtodb():
    """
    The `addtodb` function inserts a message into a database with the provided content, role, chat ID,
    clear number, and time created.
    :return: a response with the content "inserted!" and the content type "text".
    """
    data = request.json
    message_id = data.get("message_id", None)
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
        "credential_token": credential_token
    }

    print("adding ", message_to_upload, " to db")
    uploaded_message, _ = DataBase().insert_message(message_to_upload)
    return jsonify({"message_id": uploaded_message.mes_id,
                    "content": content,
                    "role": role,
                    "chat": chat_k_id,
                    "clear_number": clear_number,
                    "time_created": time_created,
                    "credential_token": credential_token})


# @data_bp.route("/getfromdb", methods=["POST", "GET"])
# def getfromdb():
#     """
#     The function `getfromdb()` retrieves data from a form, checks if the username and password match a
#     specific value, and returns a rendered template based on the result.
#     :return: either a rendered template for displaying messages or a rendered template string for
#     displaying an error message.
#     """
#     data = request.form
#     username = data.get("lusername", "nan")
#     passcode = data.get("lpassword", "nan")
#     if username == os.getenv('ROOT_USER') and passcode == os.getenv('ROOT_PW'):
#         # messages_arr = messageDatabase.execute_sql(
#         #     "SELECT * FROM lmessages ORDER BY chat_key, clear_number, time_created",
#         #     True,
#         # ) ## TODO : modify
#         messages_arr = DataBase().all_messages()
#         renderedString = DataBase().parse_messages(messages_arr)
#         return flask.render_template(
#             "display_messages.html", renderedString=renderedString
#         )
#     else:
#         return flask.render_template_string(
#             'Error, please <a href="/static/display_db.html">Go back</a>'
#         )


@data_bp.route("/addmessagefeedback", methods=["POST", "GET"])
def addmessagefeedback():
    data = request.json
    message_id = data.get("message_id")
    if message_id is None:
        return jsonify({"message": "error"}), 404
    feedback_content = data.get("content")
    print(feedback_content)
    print(message_id)
    feedback, _ = DataBase().insert_feedback(FeedbackModel(feedback_content=feedback_content, message_id=message_id))
    return jsonify({"message_id": message_id, "feedback_id": feedback.feedback_id, "feedback_content": feedback_content}), 200


@data_bp.route("/getfromdbng", methods=["POST", "GET"])
def getfromdbng():
    """
    The function `getfromdbng` retrieves messages from a database if the provided username and password
    match the credentials for the root user.
    :return: a JSON response. If the username and passcode are os.getenv('ROOT_USER') and os.getenv('ROOT_PW') respectively, it will
    return a JSON object with a "message" key set to "success" and a "messages" key containing an array
    of messages. If the username and passcode do not match, it will return a JSON object with a
    "message" key set to "error".
    """
    data = request.json
    username = data.get("lusername", "nan")
    passcode = data.get("lpassword", "nan")
    print(data)
    print(username, passcode)
    if username == os.getenv('ROOT_USER') and passcode == os.getenv('ROOT_PW'):
        messages_arr = DataBase().all_messages()
        return jsonify({"message": "success", "messages": messages_arr})
    else:
        return jsonify({"message": "error"})


# @data_bp.route("/exesql", methods=["POST", "GET"])
# def exesql():
#     data = request.json
#     username = data["lusername"]
#     passcode = data["lpassword"]
#     sqlexec = data["lexesql"]
#     if username == os.getenv('ROOT_USER') and passcode == os.getenv('ROOT_PW'):
#         messages_arr = messageDatabase.execute_sql(sqlexec) ## TODO : modify
#         return Response(f"{messages_arr}", 200)
#     else:
#         return Response("wrong password", 404)


@data_bp.route("/delete_uploaded_data", methods=["POST"])
def delete_uploaded_data():
    """
    The function `delete_uploaded_data` deletes a data source with a given collection name from a
    database.
    :return: a JSON response with the key "deleted" and the value being the name of the collection that
    was deleted.
    """
    data = request.json
    collection_name = data["collection"]
    db.delete_datasource_chroma(collection_name)
    return jsonify({"deleted": collection_name})


@data_bp.route("/delete_doc", methods=["POST"])
@flask_login.login_required
def delete_doc():
    """
    The `delete_doc` function deletes a document from a specified collection in a database.
    :return: a JSON response containing the name of the deleted document and the name of the collection
    it was deleted from.
    """
    data = request.json
    collection_name = data["collection"]
    doc_name = data["doc"]

    collection = db.client.get_collection(name=collection_name)
    print(collection)
    collection.delete(where={"from_doc": doc_name})
    print("deleted")
    return jsonify({"deleted": doc_name, "from_collection": collection_name})


@data_bp.route("/add_doc_tosection", methods=["POST"])
@flask_login.login_required
def add_fromdoc_tosection():
    """
    The function `add_fromdoc_tosection` adds a URL to a specific section in a collection and returns a
    JSON response indicating the URL that was added and the collection it was added to.
    :return: a JSON response containing the URL that was added and the name of the collection it was
    added to.
    """
    data = request.json
    collection_name = data["collection"]
    section_id = data["section_id"]
    url_to_add = data["url_to_add"]

    DataBase().update_section_add_fromdoc(section_id=section_id, from_doc=url_to_add)
    # messageDatabase.update_section_add_fromdoc(
    #     section_id=section_id, from_doc=url_to_add
    # ) ## TODO : modify
    return jsonify({"added": url_to_add, "to_collection": collection_name})


@data_bp.route("/get_section", methods=["POST"])
def get_section():
    """
    The function `get_section` retrieves a specific section from a collection and returns the section
    details along with the pulling_from information.
    :return: a JSON object that contains the sections and the pulling_from values.
    """
    data = request.json
    collection_name = data["collection"]
    section_id = data["section_id"]

    # sections = messageDatabase.execute_sql(
    #     f"SELECT * FROM lsections WHERE section_id = '{section_id}'"
    # ) ## TODO : modify
    sections, _ = DataBase().get_sections_by_id(section_id=section_id)
    pfrom = [s.pulling_from for s in sections]
    return jsonify({"sections": sections, "pulling_from": pfrom})
