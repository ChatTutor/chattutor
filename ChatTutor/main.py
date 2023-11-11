import flask
from flask import Flask, request, redirect, send_from_directory, url_for
from flask import stream_with_context, Response, abort, jsonify
from flask_cors import CORS
from nice_functions import pprint, time_it 
from core.extensions import (
    db,
    user_db,
    get_random_string,
    generate_unique_name,
    stream_text,
)  # Importing the database object from extensions module
from core.tutor import Tutor
from core.tutor import cqn_system_message, default_system_message, interpreter_system_message
import json
import time
import os
from core.reader import URLReader
from core.definitions import Text
from core.definitions import Doc
from core.reader import parse_plaintext_file
import io
import uuid
from werkzeug.datastructures import FileStorage

# import pymysql
import sqlite3
import openai
from core.reader import read_filearray, extract_file,parse_plaintext_file
from datetime import datetime
from core.messagedb import MessageDB
import interpreter
from url_reader import URLReader
from core.definitions import Text
from core.definitions import Doc
import io
import uuid
from werkzeug.datastructures import FileStorage
# import markdown

# from vectordatabase import VectorDatabase

interpreter.auto_run = True
from core.openai_tools import load_api_keys
load_api_keys()


app = Flask(__name__)
CORS(app, resources={r"/ask": {"origins": "https://barosandu.github.io"}})
# CORS(app)  # Enabling CORS for the Flask app to allow requests from different origins
db.init_db()
user_db.init_db()

messageDatabase = MessageDB(
    host="34.41.31.71",
    user="admin",
    password="AltaParolaPuternica1245",
    database="chatmsg",
    statistics_database="sessiondat",
)

# Only for deleting the db when you first access the site. Can be used for debugging
presetTables1 = """
    DROP TABLE IF EXISTS lchats
"""
# only for deleting the db when you first access the site. Can be used for debugging
presetTables2 = """
    DROP TABLE IF EXISTS lmessages
"""

chats_table_Sql = """
CREATE TABLE IF NOT EXISTS lchats (
    chat_id text PRIMARY KEY
    )"""


def connect_to_database():
    """Function that connects to the database"""
    # for mysql server
    # connection = pymysql.connect(
    #     host='localhost',
    #     user='root',
    #     password='password',
    #     db='mydatabase',
    #     charset='utf8mb4',
    #     cursorclass=pymysql.cursors.DictCursor
    # )
    # return connection
    return sqlite3.connect("chat_store.sqlite3")


messages_table_Sql = """
CREATE TABLE IF NOT EXISTS lmessages (
    mes_id text PRIMARY KEY,
    role text NOT NULL,
    content text NOT NULL,
    chat_key integer NOT NULL,
    FOREIGN KEY (chat_key) REFERENCES lchats (chat_id)
    )"""


def initialize_ldatabase():
    """Creates the tables if they don't exist"""
    con = sqlite3.connect("chat_store.sqlite3")
    cur = con.cursor()
    # cur.execute(presetTables1)
    # cur.execute(presetTables2)
    cur.execute(chats_table_Sql)
    cur.execute(messages_table_Sql)


initialize_ldatabase()


@app.route("/")
def index():
    """
    Serves the landing page of the web application which provides
    the ChatTutor interface. Users can ask the Tutor questions and it will
    response with information from its database of papers and information.
    Redirects the root URL to the index.html in the static folder
    """
    return redirect(url_for("static", filename="index.html"))


@app.route("/cqn")
def cqn():
    """
    Serves the landing page of the web application which provides
    the ChatTutor interface. Users can ask the Tutor questions and it will
    response with information from its database of papers and information.
    Redirects the root URL to the index.html in the static folder
    """

    load_api_keys()
    tutor = Tutor(db)
    db.load_datasource("test_embedding_basic")
    print("getting number of documents...")
    docs = db.datasource.get(include=[])
    total_papers = len(docs["ids"]) 
    pprint("total_papers", total_papers)
    print("generating welcoming message...")

    welcoming_message = f"""
                <p>Welcome to the Center for Quantum Networks (CQN) website! I am your Interactive Research Assistant, here to assist you in exploring the wealth of knowledge within the CQN research database. With access to a vast collection of <b>{total_papers}</b> research papers, I am equipped to provide insightful and accurate responses to your queries.</p>
                <p>Whether you are looking for papers by a specific author, papers from a particular date or journal, or papers related to a specific topic or subject, I've got you covered. I can also help you find similar papers to ones you already know or even provide paper summaries.</p>
                <p>Here are some examples of questions you can ask:</p>
                <ul>
                    <li>Can you summarize the content of the database?</li>
                    <li>Can you list all papers present in the database?</li>
                    <li>Can you find papers authored by X?</li>
                    <li>What papers were published in the year 2020?</li>
                    <li>Which is the most recent paper by X?</li>
                    <li>Can you recommend papers related to quantum entanglement?</li>
                    <li>Are there any similar papers to the one titled 'Entanglement-enhanced testing of multiple quantum hypotheses'?</li>
                    <li>Can you summarize the paper titled 'Quantum Networking Protocols' for me?</li>
                </ul>
                <p>Feel free to explore the CQN research database and ask any questions you may have. I'm here to assist you on your research journey!</p>    
    """
    
    # welcoming_message = "" # disable to generate a new one using simple_gpt
    if welcoming_message == "":
        welcoming_message =  time_it(tutor.simple_gpt)(f"""
        You are embedded into the Center for Quantum Networks (CQN) website as an Interactive Research Assistant. 
        Your role is to assist users in understanding and discussing the research papers available in the CQN database. 
        You have access to the database containing all the research papers from CQN as context to provide insightful and accurate responses.
        Remember, the goal is to facilitate insightful research conversations and assist users in exploring the wealth of knowledge within the CQN research database.
        The total number of papers you know is {total_papers}
        
        You can:
        - search papers by author, date, journal
        - search papers related to a topic or subject
        - find similar papers to others
        - summarize articles
        """, "Make an introductory message of yourself mentioning who you are, how many papers do you know, and what you can do to help users. Also, give examples of questions to related to what you can do. Do it in 200 words and generate the response in HTML",
        models_to_try = ["gpt-3.5-turbo"])


    return flask.render_template(
        "cqn.html", welcoming_message=welcoming_message
    )


@app.route("/chattutor")
def chattutor():
    """
    Serves the landing page of the web application which provides
    the ChatTutor interface. Users can ask the Tutor questions and it will
    response with information from its database of papers and information.
    Redirects the root URL to the index.html in the static folder
    """
    return redirect(url_for("static", filename="chattutor.html"))


@app.route("/interpreter")
def interpreter():
    """
    Serves the landing page of the web application which provides
    the ChatTutor interface. Users can ask the Tutor questions and it will
    response with information from its database of papers and information.
    Redirects the root URL to the index.html in the static folder
    """
    return redirect(url_for("static", filename="interpreter.html"))


@app.route("/static/<path:path>")
def serve_static(path):
    """Serving static files from the 'static' directory"""
    return send_from_directory("static", path)


@app.route("/ask", methods=["POST", "GET"])
def ask():
    """Route that facilitates the asking of questions. The response is generated
    based on an embedding.

    URLParams:
        conversation (List({role: ... , content: ...})):  snapshot of the current conversation
        collection: embedding used for vectorization
    Yields:
        response: {data: {time: ..., message: ...}}
    """
    data = request.json
    conversation = data["conversation"]
    collection_name = data.get("collection")
    collection_desc = data.get("description")
    multiple = data.get("multiple")
    from_doc = data.get("from_doc")
    selected_model = data.get("selectedModel")
    if selected_model == None:
        selected_model = 'gpt-3.5-turbo-16k'
    # TEMP CHANGE
    selected_model = 'gpt-4'
    print('SELECTED MODEL:', selected_model)
    print(collection_name)
    # Logging whether the request is specific to a document or can be from any document
    chattutor = Tutor(db)
    if collection_name:
        if multiple == None:
            name = collection_desc if collection_desc else ""
            chattutor.add_collection(collection_name, name)
        else:
            chattutor = Tutor(db, system_message=cqn_system_message)
            for cname in collection_name:
                message = (
                    f"CQN papers "
                    if cname == "test_embedding"
                    else """Use the following user uploaded files to provide information if asked about content from them. 
                User uploaded files """
                )
                chattutor.add_collection(cname, message)
    generate = chattutor.stream_response_generator(
        conversation, from_doc, selected_model
    )
    return Response(stream_with_context(generate()), content_type="text/event-stream")


@app.route("/ask_interpreter", methods=["POST", "GET"])
def ask_interpreter():
    """Route that facilitates the asking of questions. The response is generated
    based on an embedding.

    URLParams:
        conversation (List({role: ... , content: ...})):  snapshot of the current conversation
        collection: embedding used for vectorization
    Yields:
        response: {data: {time: ..., message: ...}}
    """
    data = request.json
    conversation = data["conversation"]
    collection_name = data.get("collection")
    collection_desc = data.get("description")
    multiple = data.get("multiple")
    from_doc = data.get("from_doc")
    selected_model = data.get("selectedModel")
    if selected_model == None:
        # selected_model = 'gpt-3.5-turbo-16k'
        selected_model = "gpt-4"
    print("SELECTED MODEL:", selected_model)
    print(collection_name)
    # Logging whether the request is specific to a document or can be from any document
    chattutor = Tutor(db)
    if collection_name:
        if multiple == None:
            name = collection_desc if collection_desc else ""
            chattutor.add_collection(collection_name, name)
        else:
            chattutor = Tutor(db, system_message=interpreter_system_message)
            for cname in collection_name:
                message = (
                    f"CQN papers "
                    if cname == "test_embedding"
                    else """Use the following user uploaded files to provide information if asked about content from them. 
                User uploaded files """
                )
                chattutor.add_collection(cname, message)
    generate = chattutor.stream_interpreter_response_generator(
        conversation, from_doc, selected_model
    )
    return stream_with_context(generate())


@app.route("/addtodb", methods=["POST", "GET"])
def addtodb():
    data = request.json
    content = data["content"]
    role = data["role"]
    chat_k_id = data["chat_k"]
    clear_number = data["clear_number"]
    time_created = data["time_created"]
    messageDatabase.insert_chat(chat_k_id)
    message_to_upload = {
        "content": content,
        "role": role,
        "chat": chat_k_id,
        "clear_number": clear_number,
        "time_created": time_created,
    }
    messageDatabase.insert_message(message_to_upload)
    return Response("inserted!", content_type="text")


@app.route("/getfromdb", methods=["POST", "GET"])
def getfromdb():
    data = request.form
    username = data.get("lusername", "nan")
    passcode = data.get("lpassword", "nan")
    print(data)
    print(username, passcode)
    if username == "root" and passcode == "admin":
        messages_arr = messageDatabase.execute_sql(
            "SELECT * FROM lmessages ORDER BY chat_key, clear_number, time_created",
            True,
        )
        renderedString = messageDatabase.parse_messages(messages_arr)
        return flask.render_template(
            "display_messages.html", renderedString=renderedString
        )
    else:
        return flask.render_template_string(
            'Error, please <a href="/static/display_db.html">Go back</a>'
        )


@app.route("/exesql", methods=["POST", "GET"])
def exesql():
    data = request.json
    username = data["lusername"]
    passcode = data["lpassword"]
    sqlexec = data["lexesql"]
    if username == "root" and passcode == "admin":
        messages_arr = messageDatabase.execute_sql(sqlexec)
        return Response(f"{messages_arr}", 200)
    else:
        return Response("wrong password", 404)


@app.route("/compile_chroma_db", methods=["POST"])
def compile_chroma_db():
    from core import loader

    token = request.headers.get("Authorization")
    if token != openai.api_key:
        abort(401)  # Unauthorized

    loader.init_chroma_db()
    return "Chroma db created successfully", 200


@app.route("/upload_data_to_process", methods=["POST"])
def upload_data_to_process():
    file = request.files.getlist("file")
    print(file)
    data = request.form
    desc = data["name"].replace(" ", "-")
    if len(desc) == 0:
        desc = "untitled" + "-" + get_random_string(5)
    resp = {"collection_name": False}
    print("File,", file)
    if file[0].filename != "":
        files = []
        for f in file:
            files = files + extract_file(f)
            print(f"Extracted file {f}")
        texts = read_filearray(files)
        # Generating the collection name based on the name provided by user, a random string and the current
        # date formatted with punctuation replaced
        collection_name = generate_unique_name(desc)

        db.load_datasource(collection_name)
        db.add_texts(texts)
        resp["collection_name"] = collection_name

    return jsonify(resp)



@app.route("/upload_data_from_drop", methods=["POST"])
def upload_data_from_drop():
    cname = request.form.get('collection_name')
    file = request.files.getlist('file')
    f_arr = []
    for fil in file:
        f_arr.append(fil.filename)

    resp = {"collection_name": cname, "files_uploaded_name": f_arr}
    if file[0].filename != "":
        files = []
        for f in file:
            files = files + extract_file(f)
            print(f"Extracted file {f}")

        texts = read_filearray(files)
        # Generating the collection name based on the name provided by user, a random string and the current
        # date formatted with punctuation replaced
        print(cname)
        db.load_datasource(cname)
        db.add_texts(texts)

    return jsonify(resp)

@app.route("/delete_uploaded_data", methods=["POST"])
def delete_uploaded_data():
    data = request.json
    collection_name = data["collection"]
    db.delete_datasource_chroma(collection_name)
    return jsonify({"deleted": collection_name})

@app.route("/upload_site_url", methods=["POST"])
def upload_site_url():
    ajson = request.json
    coll_name = ajson['name']
    url_to_parse = ajson["url"]
    print('UTP: ', url_to_parse)
    collection_name = coll_name
    resp = {"collection_name": coll_name, "urls": url_to_parse}
    for surl in url_to_parse:
        ss = URLReader.parse_url(surl)        
        site_text = f"{ss.encode('utf-8', errors='replace')}"
        navn = f"thingBoi{uuid.uuid4()}"
        file = FileStorage(stream=io.BytesIO(bytes(site_text, 'utf-8')), name=navn)

        f_f = (file, navn)
        doc = Doc(docname=f_f[1], citation="", dockey=f_f[1])
        texts = parse_plaintext_file(f_f[0], doc=doc, chunk_chars=2000, overlap=100)
        db.load_datasource(collection_name)
        db.add_texts(texts)
    return jsonify(resp)







if __name__ == "__main__":
    app.run(debug=True, port=5000)  # Running the app in debug mode
