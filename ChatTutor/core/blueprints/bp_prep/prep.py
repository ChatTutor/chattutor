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
    code = data.get('code', None)
    if code is not None:
        accesscode, _ = DataBase().get_access_code_by_code(code)
        user_id = accesscode['id']
        user, _ = DataBase().get_users_by_id(uid=user_id)
        if len(user) > 0:
            usr = user[0]
            usrjson = usr.jsonserialize()
            return jsonify({'message': 'success', 'email': usr.email, 'id': usr.user_id})
        else:
            return jsonify({'message': 'error2'})
    else:
        return jsonify({'message': 'error'})


@prep_bp.route("/course/register", methods=["POST", "GET"])
@flask_login.login_required
def urlcrawler():
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
