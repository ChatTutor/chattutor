import flask
from flask import Flask, request, redirect, send_from_directory, url_for, render_template
from flask import stream_with_context, Response, abort, jsonify
from flask_cors import CORS
from itsdangerous import URLSafeTimedSerializer
from flask import Blueprint, render_template
from core.tutor import Tutor
from core.tutor import cqn_system_message, default_system_message, interpreter_system_message
import json
from nice_functions import pprint, time_it
from core.extensions import (
    db,
    user_db,
    messageDatabase,
    get_random_string,
    generate_unique_name,
    stream_text,
) 
from core.definitions import Text
from core.definitions import Doc
from core.reader import parse_plaintext_file
import io
import uuid
from werkzeug.datastructures import FileStorage
import re
# import pymysql
import sqlite3
import openai
import core.loader
from core.reader import read_filearray, extract_file, parse_plaintext_file_read
from datetime import datetime
from core.messagedb import MessageDB
import interpreter
from core.definitions import Text
from core.definitions import Doc
import io
import uuid
from werkzeug.datastructures import FileStorage
# import markdown
import flask_login

data_bp = Blueprint('bp_data', __name__)


@data_bp.route("/addtodb", methods=["POST", "GET"])
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


@data_bp.route("/getfromdb", methods=["POST", "GET"])
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


@data_bp.route("/getfromdbng", methods=["POST", "GET"])
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
    


@data_bp.route("/exesql", methods=["POST", "GET"])
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


@data_bp.route("/delete_uploaded_data", methods=["POST"])
def delete_uploaded_data():
    data = request.json
    collection_name = data["collection"]
    db.delete_datasource_chroma(collection_name)
    return jsonify({"deleted": collection_name})


@data_bp.route("/delete_doc", methods=["POST"])
@flask_login.login_required
def delete_doc():
    data = request.json
    collection_name = data["collection"]
    doc_name = data["doc"]

    collection = db.client.get_collection(name=collection_name)
    print(collection)
    collection.delete(where={'from_doc': doc_name})
    print("deleted")
    return jsonify({"deleted": doc_name, "from_collection": collection_name})

@data_bp.route("/add_doc_tosection", methods=["POST"])
@flask_login.login_required
def add_fromdoc_tosection():
    data = request.json
    collection_name = data["collection"]
    section_id = data["section_id"]
    url_to_add = data["url_to_add"]

    messageDatabase.update_section_add_fromdoc(section_id=section_id, from_doc=url_to_add)
    return jsonify({"added": url_to_add, "to_collection": collection_name})


@data_bp.route("/get_section", methods=["POST"])
def get_section():
    data = request.json
    collection_name = data["collection"]
    section_id = data["section_id"]

    sections = messageDatabase.execute_sql(
        f"SELECT * FROM lsections WHERE section_id = '{section_id}'"
    )
    pfrom = [s["pulling_from"] for s in sections]
    return jsonify({'sections': sections, 'pulling_from': pfrom})

