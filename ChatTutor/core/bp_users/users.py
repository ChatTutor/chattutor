# import pymysql
import uuid

import bcrypt
import flask
import flask_login
from core.extensions import (messageDatabase)
from flask import (Blueprint, jsonify, request)

users_bp = Blueprint("bp_users", __name__)

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
    email = "NO NAME"
    password_hash = "NO NUMBER"
    google_id = ""
    name = ""

    def get_id(self):
        return self.email

    @property
    def password(self):
        raise AttributeError("password not readable")

    @password.setter
    def password(self, password):
        self.password_hash = bcrypt.hashpw(
            password.encode("utf-8", "ignore"), bcrypt.gensalt()
        )

    def verify_password(self, p):
        print(
            self.password_hash,
            bcrypt.hashpw(p.encode("utf8", "ignore"), bcrypt.gensalt()).decode("utf-8"),
        )
        print(
            self.password_hash,
            bcrypt.hashpw(p.encode("utf8", "ignore"), bcrypt.gensalt()).decode("utf-8"),
        )
        print(self.password_hash.encode("utf-8"), p.encode("utf-8"))
        return bcrypt.checkpw(p.encode("utf-8"), self.password_hash.encode("utf-8"))


@users_bp.route('/auth/google', methods=['POST'])
def oauth_register():
    user_info = request.json
    google_id = user_info.get('google_id')
    email = user_info.get('email')
    name = user_info.get('name')

    if not google_id or not email or not name:
        return jsonify({"error": "Missing information from Google OAuth"}), 400

    # Register user if it doesn't exist
    user = messageDatabase.get_user(email=email)
    if len(user) == 0:
        user = User()
        user.google_id = google_id
        user.email = email
        user.name = name
        try:
            messageDatabase.insert_oauth_user(user)
            return jsonify({'message': 'User created', 'user': {'google_id': google_id, 'email': email, 'name': name}}), 201
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    return jsonify({'message': 'User logged in', 'user': {'google_id': google_id, 'email': email, 'name': name}}), 201

@users_bp.route("/register", methods=["POST"])
def register_user():
    """
    The function `register_user()` registers a new user by retrieving their email and
    password from a form, checking if the email already exists in the database, creating a new User
    object with the provided information, and inserting the user into the database.
    :return: a string message indicating the result of the user registration process. If the email
    already exists in the database, it returns a message stating that the email already exists. If
    the registration is successful, it returns a message indicating that the user has been inserted and
    provides a link to the login page.
    """
    email = flask.request.form["email"]
    password = flask.request.form["password"]

    email = flask.request.form["email"]
    users = messageDatabase.get_user(email=email)

    if len(users) != 0:
        return f"Email {email} already exists!"

    print(password)
    user = User()
    user.email = email
    user.password = password
    user.user_type = "PROFESSOR"
    print(user.password_hash)
    messageDatabase.insert_user(user)
    return f'User {user} inserted, please <a href="/login">Login</a>'


@users_bp.route("/login", methods=["POST"])
def login():
    """
    The login function checks if the email and password provided by the user match the stored
    email and password in the database, and logs the user in if they match.
    :return: The function `login()` returns either 'Invalid email', 'Bad login, <a
    href="/">Return</a>', or a redirect to "/protected" depending on the conditions met in the code.
    """
    email = flask.request.form["email"]
    users = messageDatabase.get_user(email=email)
    if len(users) == 0:
        return "Invalid email"
    print(users[0]["password"])
    user = User()
    user.email = users[0]["email"]
    user.password_hash = users[0]["password"]
    if user.verify_password(flask.request.form["password"]):
        flask_login.login_user(user)
        return flask.redirect("/protected")
    return 'Bad login, <a href="/">Return</a>'


@users_bp.route("/protected")
@flask_login.login_required
def protected():
    return f'Logged in as: {flask_login.current_user.email}, <a href="/">Return</a>'


@users_bp.route("/logout")
def logout():
    """
    The function `logout` logs out the user and returns a message with a link to return to the homepage.
    :return: The string 'Logged out, <a href="/">Return</a>' is being returned.
    """
    flask_login.logout_user()
    return 'Logged out, <a href="/">Return</a>'


@users_bp.route("/getuser", methods=["POST"])
@flask_login.login_required
def getuser():
    """
    The function `getuser` prints the email of the currently logged in user and returns it as a JSON
    object.
    :return: a JSON object containing the email of the currently logged in user.
    """
    print("Logged in as", flask_login.current_user.email)
    return jsonify({"email": flask_login.current_user.email})


@users_bp.route("/isloggedin", methods=["POST"])
def isloggedin():
    """
    The function checks if the current user is logged in and returns a JSON response indicating whether
    they are logged in or not.
    :return: The function isloggedin() returns a JSON object with a key-value pair indicating whether
    the user is logged in or not. If the current user is authenticated, it returns {'loggedin': True},
    otherwise it returns {'loggedin': False}.
    """
    print(flask_login.current_user)
    if flask_login.current_user.is_authenticated:
        return jsonify({"loggedin": True})
    return jsonify({"loggedin": False})


@users_bp.route("/users/<email>/mycourses", methods=["POST"])
@flask_login.login_required
def getusercourses(email):
    """
    The function `getusercourses` retrieves the courses associated with a given email and returns
    them in JSON format.

    :param email: The `email` parameter is the email of the user for whom you want to retrieve
    the courses
    :return: a JSON response containing the courses associated with the given email.
    """
    if email != flask_login.current_user.email:
        return 'Not allowed, <a href="/">Return</a>'
    courses = messageDatabase.get_user_courses(email=email)
    return jsonify({"courses": courses})


@users_bp.route("/users/<email>/courses/<course>", methods=["POST"])
@flask_login.login_required
def getusercoursessections(email, course):
    """
    The function `getusercoursessections` returns the sections of a given course for a specific user,
    but only if the email matches the currently logged in user.

    :param email: The `email` parameter is the email of the user for whom we want to retrieve
    the courses and sections. It is used to check if the user is authorized to access the information
    :param course: The "course" parameter is the ID or name of the course for which you want to retrieve
    the sections
    :return: a JSON object containing the sections of a specific course.
    """
    if email != flask_login.current_user.email:
        return 'Not allowed, <a href="/">Return</a>'
    sections = messageDatabase.get_courses_sections_format(course_id=course)
    return jsonify({"sections": sections})


@users_bp.route("/users/<email>/coursesv1/<course>", methods=["POST"])
@flask_login.login_required
def getusercoursessectionsv1(email, course):
    """
    The function `getusercoursessectionsv1` returns the sections of a given course for a specific user,
    but only if the user is currently logged in.

    :param email: The email parameter is the email of the user for whom we want to retrieve the
    course sections
    :param course: The "course" parameter is the ID or name of the course for which you want to retrieve
    the sections
    :return: a JSON object containing the sections of a given course.
    """
    if email != flask_login.current_user.email:
        return 'Not allowed, <a href="/">Return</a>'
    sections = messageDatabase.get_courses_sections(course_id=course)
    return jsonify({"sections": sections})


@users_bp.route("/student/register", methods=["POST"])
def student_register():
    """
    The function `student_register` registers a new student user by retrieving the email and
    password from a form, creating a new User object with the
    provided information, and inserting the user into the message database.
    :return: a string message indicating the result of the user registration process. If the email
    already exists in the database, it returns a message stating that the email already exists. If
    the registration is successful, it returns a message indicating that the user has been inserted and
    provides a link to the login page.
    """
    email = flask.request.form["email"]
    password = flask.request.form["password"]

    email = flask.request.form["email"]
    users = messageDatabase.get_user(email=email)

    if len(users) != 0:
        return f"email {email} already exists!"

    print(password)
    user = User()
    user.email = email
    user.password = password
    user.user_type = "STUDENT"
    print(user.password_hash)
    messageDatabase.insert_user(user)
    return f'User {user} inserted, please <a href="/login">Login</a>'


@users_bp.route("/course/addtoken", methods=["POST"])
@flask_login.login_required
def addtoken():
    """
    The function `addtoken()` takes in form data, extracts the necessary values, inserts them into a
    database, and redirects the user to a specific course page.
    :return: a Flask redirect to the "/courses/{cid}" route.
    """
    args = flask.request.form
    print(args)
    cid = args.get("course_id")
    curl = args.get("course_url")
    rulocally = 1 if (args.get("run_locally", "off") == "on") else 0
    testmode = 1 if (args.get("test_mode", "off") == "on") else 0
    isstatic = 1 if (args.get("is_static", "off") == "on") else 0
    buildwith = args.get("built_with", "Other")
    server_port = args.get("server_port", 0)
    chattutor_server = args.get("chattutor_server", "http://127.0.0.1")
    token_id = f"{uuid.uuid4()}"
    isdef = 1 if (args.get("is_default", "off") == "on") else 0

    print(
        flask_login.current_user.email,
        cid,
        curl,
        rulocally,
        testmode,
        isstatic,
        buildwith,
        server_port,
        chattutor_server,
        token_id,
        isdef,
    )
    messageDatabase.insert_config(
        flask_login.current_user.email,
        cid,
        curl,
        rulocally,
        testmode,
        isstatic,
        buildwith,
        server_port,
        chattutor_server,
        token_id,
        isdef,
    )
    return flask.redirect(f"/courses/{cid}")


@users_bp.route("/course/<cid>/gettokens", methods=["POST"])
@flask_login.login_required
def gettokens(cid):
    """
    The function `gettokens` retrieves tokens from the message database based on a given course ID and
    returns them as a JSON response.

    :param cid: The parameter "cid" stands for "course id". It is used to identify a specific course in
    the message database
    :return: a JSON response containing the tokens retrieved from the message database for the given
    course ID.
    """
    tokens = messageDatabase.get_config_by_course_id(cid)
    return jsonify(tokens)


@users_bp.route("/gendefaulttoken", methods=["POST"])
@flask_login.login_required
def gendefaulttoken():
    """
    The function `gendefaulttoken()` retrieves default configuration tokens for a given URL and returns
    them as a JSON response.
    :return: a JSON response containing the tokens retrieved from the message database for the given
    request URL.
    """
    request_url = request.url
    tokens = messageDatabase.get_default_config_for_url(request_url)
    return jsonify(tokens)
