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
from flask import Blueprint, render_template
from core.tutor import Tutor
from core.tutor import (
    cqn_system_message,
    default_system_message,
    interpreter_system_message,
)
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

prep_bp = Blueprint("bp_prep", __name__)


@prep_bp.route("/course/register", methods=["POST", "GET"])
@flask_login.login_required
def urlcrawler():
    """
    The function `urlcrawler` crawls a given URL and saves the parsed data to a database, along with
    additional information such as course name and professor.
    :return: a Response object.
    """
    data = request.json
    url: str = data.get("url_to_parse", "https://www.google.com")
    course_name: str = data.get("course_name", "No course")
    proffessor: str = data.get("proffessor", "No professor")
    collection_name: str = data.get("collection_name", f"{uuid.uuid4()}")

    url_r = URLSpider(1, 200)
    url_r.set_thread_count(25)
    url_r.set_bfs_thread_count(25)
    url_r.MAX_LEVEL_PARQ = 2
    course_id = f"{uuid.uuid4()}"
    pprint(f"Crawling... {url_r.max_number_of_urls}")

    return Response(
        stream_with_context(
            url_r.new_spider_function(
                urltoapp=url,
                save_to_database=db,
                collection_name=collection_name,
                message_db=messageDatabase,
                course_name=course_name,
                proffessor=proffessor,
                course_id=course_id,
                current_user=flask_login.current_user,
            )
        )
    )


@prep_bp.route("/course/parse", methods=["POST", "GET"])
def genbfsarray():
    """
    The function `genbfsarray` takes a JSON request, extracts a URL from it (defaulting to
    "https://www.google.com" if no URL is provided), and uses a URLSpider object to crawl the website
    and generate a breadth-first search array.
    :return: the result of `url_r.get_bfs_array(url)` as a JSON response.
    """
    data = request.json
    url: str = data.get("url_to_parse", "https://www.google.com")

    url_r = URLSpider(1, 200)
    url_r.set_thread_count(25)
    url_r.set_bfs_thread_count(20)
    url_r.MAX_LEVEL_PARQ = 2
    print("crawling...")

    return jsonify(url_r.get_bfs_array(url))
