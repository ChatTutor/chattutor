# import pymysql
import uuid

# import markdown
import flask_login
import re
from core.extensions import db
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
from flask import stream_with_context, Response, abort, jsonify
from flask_cors import CORS
from itsdangerous import URLSafeTimedSerializer
from urllib.parse import urlparse, ParseResult


prep_bp = Blueprint("bp_prep", __name__)


@prep_bp.route("/course/bymainpage", methods=["POST", "GET"])
def get_course_by_main_page():
    """Get course which contains sections reffered to by url

    Returns:
        URLParams:
        ```
        {
            "mainpage" : str # url of section we want
        }
        ```
    """
    data = request.json
    course_maipage = data.get("mainpage", None)
    if course_maipage is not None:
        colname, _ = DataBase().get_course_name_by_sections_mainpage(course_maipage)
        return jsonify({"collection": colname, "message": "success"})
    return jsonify({"error": 1, "message": "failure"})


@prep_bp.route("/accescodes/getuseridandemail", methods=["POST", "GET"])
def get_accescode_by_code():
    data = request.json
    code = data.get("code", None)
    if code is not None:
        accesscode, _ = DataBase().get_access_code_by_code(code)
        user_id = accesscode["id"]
        user, _ = DataBase().get_users_by_id(uid=user_id)
        if len(user) > 0:
            usr = user[0]
            usrjson = usr.jsonserialize()
            return jsonify({"message": "success", "email": usr.email, "id": usr.user_id})
        else:
            return jsonify({"message": "error2"})
    else:
        return jsonify({"message": "error"})


@prep_bp.route("/accescodes/delete_key", methods=["POST", "GET"])
def delete_accescode_key():
    data = request.json
    code = data.get("code", None)
    user_id = data.get("user_id", None)
    if code is not None and data is not None:
        DataBase().remove_acces_code(code=code, uid=user_id)
        return jsonify({"message": "success"})


@prep_bp.route("/course/parse", methods=["POST", "GET"])
def genbfsarray():
    """
    The function `genbfsarray` takes a JSON request, extracts a URL from it (defaulting to
    "https://www.google.com" if no URL is provided), and uses a URLSpider object to crawl the website
    and generate a breadth-first search array of all linked pages urls.
    URLParams:
        ```
        {
            "url_to_parse" : str # origin url (graph root)
        }
        ```
    Returns:
        TODO: document this
    """
    data = request.json
    url: str = data.get("url_to_parse", "https://www.google.com")

    url_r = URLSpider(1, 200)
    url_r.set_thread_count(25)
    url_r.set_bfs_thread_count(20)
    url_r.MAX_LEVEL_PARQ = 2
    print("crawling...")

    return jsonify(url_r.get_bfs_array(url))
