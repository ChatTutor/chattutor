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
import bcrypt
users_bp = Blueprint('bp_users', __name__)

# def generate_token(email):
#     serializer = URLSafeTimedSerializer(app.config["SECRET_KEY"])
#     return serializer.dumps(email, salt=app.config["SECURITY_PASSWORD_SALT"])
#
#
# def confirm_token(token, expiration=3600):
#     serializer = URLSafeTimedSerializer(app.config["SECRET_KEY"])
#     try:
#         email = serializer.loads(
#             token, salt=app.config["SECURITY_PASSWORD_SALT"], max_age=expiration
#         )
#         return email
#     except Exception:
#         return False


class User(flask_login.UserMixin):
    username = 'NO FACE'
    email = 'NO NAME'
    password_hash = 'NO NUMBER'
    user_type = ''

    def get_id(self):
        return self.username

    @property
    def password(self):
        raise AttributeError('password not readable')

    @password.setter
    def password(self, password):
        self.password_hash = bcrypt.hashpw(password.encode('utf-8', 'ignore'), bcrypt.gensalt())

    def verify_password(self, p):
        print(self.password_hash, bcrypt.hashpw(p.encode('utf8', 'ignore'), bcrypt.gensalt()).decode('utf-8'))
        print(self.password_hash, bcrypt.hashpw(p.encode('utf8', 'ignore'), bcrypt.gensalt()).decode('utf-8'))
        print(self.password_hash.encode('utf-8'), p.encode('utf-8'))
        return bcrypt.checkpw(p.encode('utf-8'), self.password_hash.encode('utf-8'))

@users_bp.route('/register', methods=['POST'])
def register_user():
    username = flask.request.form['username']
    email = flask.request.form['email']
    password = flask.request.form['password']

    email = flask.request.form['email']
    users = messageDatabase.get_user(username=username)

    if len(users) != 0:
        return f'Username {username} already exists!'

    print(password)
    user = User()
    user.email = email
    user.password = password
    user.username = username
    user.user_type = 'PROFESSOR'
    print(user.password_hash)
    messageDatabase.insert_user(user)
    return f'User {user} inserted, please <a href="/login">Login</a>'


@users_bp.route('/login', methods=['POST'])
def login():
    username = flask.request.form['username']
    users = messageDatabase.get_user(username=username)
    if len(users) == 0:
        return 'Invalid username'
    print(users[0]["password"])
    user = User()
    user.username = users[0]["username"]
    user.email = users[0]["email"]
    user.password_hash = users[0]["password"]
    if user.verify_password(flask.request.form['password']):
        flask_login.login_user(user)
        return flask.redirect("/protected")
    return 'Bad login, <a href="/">Return</a>'


@users_bp.route('/protected')
@flask_login.login_required
def protected():
    return f'Logged in as: {flask_login.current_user.username}, <a href="/">Return</a>'


@users_bp.route('/logout')
def logout():
    flask_login.logout_user()
    return 'Logged out, <a href="/">Return</a>'

@users_bp.route("/getuser", methods=['POST'])
@flask_login.login_required
def getuser():
    print('Logged in as', flask_login.current_user.username)
    return jsonify({
        'username': flask_login.current_user.username
    })

@users_bp.route("/isloggedin", methods=['POST'])
def isloggedin():
    print(flask_login.current_user)
    if flask_login.current_user.is_authenticated:
        return jsonify({
            'loggedin': True
        })
    return jsonify({
            'loggedin': False
        })

@users_bp.route("/users/<username>/mycourses", methods=['POST'])
@flask_login.login_required
def getusercourses(username):
    if username != flask_login.current_user.username:
        return 'Not allowed, <a href="/">Return</a>'
    courses = messageDatabase.get_user_courses(username=username)
    return jsonify({
        'courses': courses
    })


@users_bp.route("/users/<username>/courses/<course>", methods=['POST'])
@flask_login.login_required
def getusercoursessections(username, course):
    if username != flask_login.current_user.username:
        return 'Not allowed, <a href="/">Return</a>'
    sections = messageDatabase.get_courses_sections_format(course_id=course)
    return jsonify({
        'sections': sections
    })


@users_bp.route("/users/<username>/coursesv1/<course>", methods=['POST'])
@flask_login.login_required
def getusercoursessectionsv1(username, course):
    if username != flask_login.current_user.username:
        return 'Not allowed, <a href="/">Return</a>'
    sections = messageDatabase.get_courses_sections(course_id=course)
    return jsonify({
        'sections': sections
    })

@users_bp.route("/student/register", methods=['POST'])
def student_register():
    username = flask.request.form['username']
    email = flask.request.form['email']
    password = flask.request.form['password']

    email = flask.request.form['email']
    users = messageDatabase.get_user(username=username)

    if len(users) != 0:
        return f'Username {username} already exists!'

    print(password)
    user = User()
    user.email = email
    user.password = password
    user.username = username
    user.user_type = 'STUDENT'
    print(user.password_hash)
    messageDatabase.insert_user(user)
    return f'User {user} inserted, please <a href="/login">Login</a>'


@users_bp.route("/course/addtoken", methods=['POST'])
@flask_login.login_required
def addtoken():
    args = flask.request.form
    print(args)
    cid = args.get('course_id')
    curl = args.get('course_url')
    rulocally = 1 if (args.get('run_locally', 'off') == 'on') else 0
    testmode = 1 if (args.get('test_mode', 'off') == 'on') else 0
    isstatic = 1 if (args.get('is_static', 'off') == 'on') else 0
    buildwith = args.get('built_with', 'Other')
    server_port =  args.get('server_port', 0)
    chattutor_server =  args.get('chattutor_server', 'http://127.0.0.1')
    token_id = f'{uuid.uuid4()}'
    isdef = 1 if (args.get('is_default', 'off') == 'on') else 0


    print(flask_login.current_user.username,cid,
                                  curl,
                                  rulocally,
                                  testmode,
                                  isstatic,
                                  buildwith,
                                  server_port,
                                  chattutor_server,
                                  token_id,
                                  isdef)
    messageDatabase.insert_config(flask_login.current_user.username,cid,
                                  curl,
                                  rulocally,
                                  testmode,
                                  isstatic,
                                  buildwith,
                                  server_port,
                                  chattutor_server,
                                  token_id,
                                  isdef)
    return flask.redirect(f"/courses/{cid}")



@users_bp.route("/course/<cid>/gettokens", methods=['POST'])
@flask_login.login_required
def gettokens(cid):
    tokens = messageDatabase.get_config_by_course_id(cid)
    return jsonify(tokens)


@users_bp.route("/gendefaulttoken", methods=['POST'])
@flask_login.login_required
def gendefaulttoken():
    request_url = request.url
    tokens = messageDatabase.get_default_config_for_url(request_url)
    return jsonify(tokens)
