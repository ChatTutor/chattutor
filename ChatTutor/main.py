from typing import List
import flask
from flask import Flask, request, redirect, send_from_directory, url_for, render_template
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
from core.definitions import Text
from core.definitions import Doc
from core.reader import parse_plaintext_file
import io
import uuid
from werkzeug.datastructures import FileStorage

# import pymysql
import sqlite3
import openai
import core.loader
from core.reader import URLReader, read_array_of_content_filename_tuple, extract_file,parse_plaintext_file
from datetime import datetime
from core.messagedb import MessageDB
import interpreter
from url_reader import URLReader
from core.definitions import Text
from core.definitions import Doc
import io
import uuid
from werkzeug.datastructures import FileStorage

interpreter.auto_run = True
from core.openai_tools import load_api_keys
load_api_keys()

app = Flask(__name__, static_folder='frontend/dist/frontend/', static_url_path='')
CORS(app, resources={r"/ask": {"origins": "https://barosandu.github.io"}})  # Enabling CORS for the Flask app to allow requests from different origins
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
    print('SELECTED MODEL:', selected_model)
    print(collection_name)
    # Logging whether the request is specific to a document or can be from any document
    chattutor = Tutor(db)
    if collection_name and collection_name != []:
        if multiple == None:
            name = collection_desc if collection_desc else ""
            chattutor.add_collection(collection_name, name)
        else:
            chattutor = Tutor(db, system_message=default_system_message)
            if "test_embedding" in collection_name:
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


@app.route("/getfromdbng", methods=["POST", "GET"])
def getfromdbng():
    data = request.json
    username = data.get("lusername", "nan")
    passcode = data.get("lpassword", "nan")
    print(data)
    print(username, passcode)
    if username == "root" and passcode == "admin":
        messages_arr = messageDatabase.execute_sql(
            "SELECT * FROM lmessages ORDER BY chat_key, clear_number, time_created",
            True,
        )
        return jsonify({'message': 'success', 'messages': messages_arr})
    else:
        return jsonify({'message': 'error'})

@app.route("/compile_chroma_db", methods=["POST"])
def compile_chroma_db():
    from core.loader import init_chroma_db
    token = request.headers.get("Authorization")
    if token != openai.api_key:
        abort(401)  # Unauthorized

    init_chroma_db()
    return "Chroma db created successfully", 200


@app.route("/upload_data_from_drop", methods=["POST"])
def upload_data_from_drop():
    try:
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

        texts = read_array_of_content_filename_tuple(files)
        # Generating the collection name based on the name provided by user, a random string and the current
        # date formatted with punctuation replaced
        print(cname)
        db.load_datasource(cname)
        db.add_texts(texts)

        return jsonify(resp)
    except Exception as e:
        return jsonify({'message': 'error'})

@app.route("/delete_uploaded_data", methods=["POST"])
def delete_uploaded_data():
    data = request.json
    collection_name = data["collection"]
    db.delete_datasource_chroma(collection_name)
    return jsonify({"deleted": collection_name})

@app.route("/upload_site_url", methods=["POST"])
def upload_site_url():
    try:
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
    except Exception as e:
        return jsonify({'message': 'error'})


__angular_paths = []
__angular_default_path = "index.html"
__root = app.static_folder

@app.errorhandler(404)
def not_found_error(error):
    return send_from_directory(__root, "index.html")

print("Running @ ", __root)

for root, subdirs, files in os.walk(__root):
    if len(root) > len(__root):
        root += "/"

    for file in files:
        relativePath = str.replace(root + file, __root, "")
        __angular_paths.append(relativePath)
    print("Angular paths: [ ", __angular_paths, " ]")

# Special trick to capture all remaining routes
@app.route('/<path:path>')
@app.route('/', defaults={'path': ''})
def angular(path):    
    if path not in __angular_paths:
        path = __angular_default_path
    
    return send_from_directory(__root, path)

if __name__ == "__main__":
    app.run(debug=True, port=5000)  # Running the app in debug mode
