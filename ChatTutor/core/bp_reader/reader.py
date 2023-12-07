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
from core.url_spider import URLSpider
from core.definitions import Text
from core.definitions import Doc
import io
import uuid
from werkzeug.datastructures import FileStorage
# import markdown
import flask_login

reader_bp = Blueprint('bp_reader', __name__)


@reader_bp.route("/upload_data_to_process", methods=["POST"])
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


@reader_bp.route("/upload_data_from_drop", methods=["POST"])
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

            texts = read_filearray(files)
            # Generating the collection name based on the name provided by user, a random string and the current
            # date formatted with punctuation replaced
            print(cname)
            db.load_datasource(cname)
            db.add_texts(texts)

        return jsonify(resp)
    except Exception as e:
        return jsonify({'message': 'error'})
    

@reader_bp.route("/upload_site_url", methods=["POST"])
def upload_site_url():
    try:
        ajson = request.json
        coll_name = ajson['name']
        url_to_parse = ajson["url"]
        print('UTP: ', url_to_parse)
        collection_name = coll_name
        resp = {"collection_name": coll_name, "urls": url_to_parse, "docs": []}
        for surl in url_to_parse:
            print(surl)
            ss = URLSpider.parse_url(surl)
            site_text = f"{ss.encode('utf-8', errors='replace')}"
            navn = re.sub(r'[^A-Za-z0-9\-_]', '_', surl)
            db.load_datasource(collection_name)
            docs = db.get_chroma(from_doc=navn, n_results=1)
            if docs == None:
                continue
            if len(docs) > 0:
                resp["docs"] = resp["docs"] + [navn + "/_already_exists"]
                continue

            file = FileStorage(stream=io.BytesIO(bytes(site_text, 'utf-8')), name=navn)
            f_f = (file, navn)

            doc = Doc(docname=f_f[1], citation="", dockey=f_f[1])
            texts = parse_plaintext_file_read(f_f[0], doc=doc, chunk_chars=2000, overlap=100)
            db.load_datasource(collection_name)
            db.add_texts(texts)
            resp["docs"] = resp["docs"] + [navn]
        return jsonify(resp)
    except Exception as e:
        print(e)
        return jsonify({'message': 'error'})