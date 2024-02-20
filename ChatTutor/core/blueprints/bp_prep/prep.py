# import pymysql
import uuid

# import markdown
import flask_login
from core.extensions import (db)
from core.url_spider import URLSpider
from flask import (Blueprint, Response, jsonify, request, stream_with_context)
from nice_functions import pprint

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
