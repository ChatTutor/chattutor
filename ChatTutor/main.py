import bcrypt
from core.bp_reader.reader import reader_bp
from core.bp_prep.prep import prep_bp
from core.bp_users.users import users_bp, User
from core.bp_data.data import data_bp
from core.bp_ask.ask import ask_bp
from core.openai_tools import load_api_keys, load_env
import flask
from flask import (
    Flask,
    request,
    redirect,
    send_from_directory,
    url_for,
    render_template,
)
from flask import stream_with_context, Response, abort, jsonify
from flask_cors import CORS
from itsdangerous import URLSafeTimedSerializer

from nice_functions import pprint, time_it
from core.extensions import (
    db,
    user_db,
    messageDatabase,
    get_random_string,
    generate_unique_name,
    stream_text,
)  # Importing the database object from extensions module
from core.tutor import Tutor
from core.tutor import (
    cqn_system_message,
    default_system_message,
    interpreter_system_message,
)
import json
import time
import os
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

# ------------ INIT APP ------------

interpreter.auto_run = True


load_env()
load_api_keys()

app = Flask(__name__, static_folder="frontend/dist/frontend/",
            static_url_path="")
CORS(app, origins=["https://barosandu.github.io", "https://pymit6101-nbqjgewnea-uc.a.run.app",
     "https://byucamacholab.github.io", "https://pr4jitd.github.io", "https://introcomp.mit.edu"])
app.secret_key = "fhslcigiuchsvjksvjksgkgs"
db.init_db()
user_db.init_db()
messageDatabase.initialize_ldatabase()

app.register_blueprint(ask_bp, url_prefix="/ask")
app.register_blueprint(data_bp)
app.register_blueprint(users_bp)
app.register_blueprint(prep_bp, url_prefix="/prep")
app.register_blueprint(reader_bp)

# ------------ LOGIN ------------

login_manager = flask_login.LoginManager()
login_manager.init_app(app)


@login_manager.unauthorized_handler
def unauthorized_handler():
    return 'Unauthorized, <a href="/">Return</a>', 401


@login_manager.user_loader
def user_loader(username):
    users = messageDatabase.get_user(username=username)

    if len(users) == 0:
        return
    user = User()
    user.username = users[0]["username"]
    user.email = users[0]["email"]
    print(users[0]["password"])
    user.password_hash = users[0]["password"]

    return user


@login_manager.request_loader
def request_loader(request):
    username = request.form.get("username")

    users = messageDatabase.get_user(username=username)

    if len(users) == 0:
        return

    user = User()
    user.username = users[0]["username"]
    user.email = users[0]["email"]
    user.password_hash = users[0]["password"]

    return user


# ----------- ANGULAR -----------
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


@app.route("/api/v1/<path:path>")
def apiv1(path):
    return send_from_directory("static/api/v1", path)


@app.route("/api/v2/<path:path>")
def apiv2(path):
    return send_from_directory("static/api/v1", path)


@app.route("/scrape/<path:path>")
@app.route("/scrape", defaults={"path": ""})
@flask_login.login_required
def angular_lr(path):
    if path not in __angular_paths:
        path = __angular_default_path
    return send_from_directory(__root, path)


# Special trick to capture all remaining routes
@app.route("/<path:path>")
@app.route("/", defaults={"path": ""})
def angular(path):
    if path not in __angular_paths:
        path = __angular_default_path
    return send_from_directory(__root, path)


if __name__ == "__main__":
    app.run(debug=True, port=5000)  # Running the app in debug mode
