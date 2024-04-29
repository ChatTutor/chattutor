import bcrypt
import flask
from flask import (
    Flask,
    request,
    redirect,
    send_from_directory,
    url_for,
    render_template,
)
from core.url_spider import URLSpider
from flask import Blueprint, Response, jsonify, request, stream_with_context
from nice_functions import pprint
from core.data import (
    DataBase,
    UserModel,
    MessageModel,
    SectionModel,
    ChatModel,
    CourseModel,
    FeedbackModel,
)
from flask import stream_with_context, Response, abort, jsonify
from flask_cors import CORS
from itsdangerous import URLSafeTimedSerializer

from nice_functions import pprint, time_it
from core.extensions import (
    db,
    user_db,
    get_random_string,
    generate_unique_name,
    stream_text,
)  # Importing the database object from extensions module
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
from core.reader import read_filearray, extract_file, parse_plaintext_file_read
from datetime import datetime

# import interpreter
from core.definitions import Text
from core.definitions import Doc
import io
import uuid
from werkzeug.datastructures import FileStorage
from authlib.integrations.flask_client import OAuth
from urllib.parse import urlparse, ParseResult

# import markdown
import flask_login

# ------------ INIT APP ------------

# interpreter.auto_run = True
from core.openai_tools import load_api_keys, load_env
from core.blueprints.bp_ask.ask import ask_bp
from core.blueprints.bp_data.data import data_bp
from core.blueprints.bp_users.users import users_bp
from core.blueprints.bp_prep.prep import prep_bp
from core.blueprints.bp_reader.reader import reader_bp
from core.data import DataBase, UserModel

load_env()
load_api_keys()

app = Flask(__name__, static_folder="frontend/dist/frontend/", static_url_path="")
default_origins = [
    "http://127.0.0.1:5000",
    "https://barosandu.github.io",
    "https://pymit6101-nbqjgewnea-uc.a.run.app",
    "https://byucamacholab.github.io",
    "https://pr4jitd.github.io",
    "https://introcomp.mit.edu",
    "https://dkeathley.github.io",
    "http://localhost:5000",
]

db_origins = DataBase().get_all_courses_urls()

db_origins_parsed = []
for url in db_origins:
    if url == "":
        continue

    parsed: ParseResult = urlparse(url)
    url_origin = parsed.scheme
    if url_origin != "":
        url_origin += "://"
    if not (parsed.hostname is None):
        url_origin += parsed.hostname
        print("[+] " + url_origin + "\n")
        db_origins_parsed.append(url_origin)


print(f"[CORS ORIGINS] received: {db_origins_parsed}")

xcors = CORS(
    app,
)

# Define a list of allowed origins
def_origins = db_origins_parsed + default_origins

app.secret_key = "fhslcigiuchsvjksvjksgkgs"
db.init_db()
user_db.init_db()


# ------------ CORS -------------


# Function to check if origin is allowed
def check_origin(request):
    return True


@app.before_request
def before_request():
    if not check_origin(request):
        return jsonify({"error": "Origin not allowed"}), 403


@prep_bp.route("/course/register", methods=["POST", "GET"])
@flask_login.login_required
def urlcrawler_():
    """
    Register course in our database to use a tutor on it.
    URLParams:
        ```
        {
            "url_to_parse" : str # origin page of your course
            "course_name" : str # your course name
            "proffessor" : str # the profs namse
            "collection_name" : str # spawned collection (knowledge base) name
            "maual" : bool # true / false
            # TODO : generate collection_name automatically
        }
        ```
    Returns:
        - a stream of parsed urls as sections
    Yields:
        TODO: document this
    """
    data = request.json
    url: str = data.get("url_to_parse", "https://www.google.com")
    course_name: str = data.get("course_name", "No course")
    proffessor: str = data.get("proffessor", "No professor")
    manual: bool = data.get("manual", False)
    collection_name: str = data.get("collection_name", f"{uuid.uuid4()}")
    course_id = f"{uuid.uuid4()}"
    print("Manual", manual)
    if manual:
        print(f"[CORS] Adding {url}")
        def_origins.append(url)
        DataBase().insert_course(
            CourseModel(
                course_id=course_id,
                name=course_name,
                proffessor=proffessor,
                mainpage=url,
                collectionname=course_name,
            )
        )
        DataBase().insert_user_to_course(flask_login.current_user.user_id, course_id=course_id)
        DataBase().insert_section(
            SectionModel(
                section_id=re.sub(r"[^A-Za-z0-9\-_]", "_", url),
                pulling_from="",
                course_id=course_id,
                sectionurl=url,
            )
        )
        DataBase().establish_course_section_relationship(
            section_id=re.sub(r"[^A-Za-z0-9\-_]", "_", url), course_id=course_id
        )

        return Response(jsonify({"course_id": course_id, "collectionname": course_name}))

    url_r = URLSpider(1, 200)
    url_r.set_thread_count(25)
    url_r.set_bfs_thread_count(25)
    url_r.MAX_LEVEL_PARQ = 2
    pprint(f"Crawling... {url_r.max_number_of_urls}")
    print(f"[CORS] Adding {url}")

    parsed: ParseResult = urlparse(url)
    url_origin = parsed.scheme
    if url_origin != "":
        url_origin += "://"
    if not (parsed.hostname is None):
        url_origin += parsed.hostname
        print("[+] " + url_origin + "\n")
        db_origins_parsed.append(url_origin)
    def_origins.append(url)
    return Response(
        stream_with_context(
            url_r.new_spider_function(
                urltoapp=url,
                save_to_database=db,
                collection_name=collection_name,
                course_name=course_name,
                proffessor=proffessor,
                course_id=course_id,
                current_user=flask_login.current_user,
            )
        )
    )


app.register_blueprint(ask_bp, url_prefix="/ask")
app.register_blueprint(data_bp)
app.register_blueprint(users_bp)
app.register_blueprint(prep_bp, url_prefix="/prep")
app.register_blueprint(reader_bp)

# ------------ OAuth ------------
oauth = OAuth(app)
google = oauth.register(
    name="google",
    client_id=os.environ["OAUTH_CLIENT_ID"],
    client_secret=os.environ["OAUTH_CLIENT_SECRET"],
    access_token_url="https://accounts.google.com/o/oauth2/token",
    access_token_params=None,
    authorize_url="https://accounts.google.com/o/oauth2/auth",
    authorize_params=None,
    api_base_url="https://www.googleapis.com/oauth2/v1/",
    userinfo_endpoint="https://openidconnect.googleapis.com/v1/userinfo",
    client_kwargs={"scope": "openid email profile"},
)

# ------------ LOGIN ------------

login_manager = flask_login.LoginManager()
login_manager.init_app(app)


@login_manager.unauthorized_handler
def unauthorized_handler():
    return 'Unauthorized, <a href="/">Return</a>', 401


@login_manager.user_loader
def user_loader(email):
    users, _ = DataBase().get_users_by_email(email=email)

    if len(users) == 0:
        return
    return users[0]


@login_manager.request_loader
def request_loader(req):
    email = req.form.get("email")
    uid = req.form.get("id")

    users = []
    if email is not None:
        users, _ = DataBase().get_users_by_email(email=email)
    if uid is not None:
        users, _ = DataBase().get_users_by_id(uid=uid)

    if len(users) == 0:
        return

    return users[0]


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


# testing
if __name__ == "__main__":
    app.run(debug=True, port=5000)  # Running the app in debug mode
