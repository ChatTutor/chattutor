# import pymysql
import uuid

import bcrypt
import flask
import flask_login
from flask import Blueprint, jsonify, request, redirect
from core.data.DataBase import UserModel
from core.data.models.AccessCodes import AccessCodeModel
from core.utils.email import EmailSender
from core.data.models import Connection

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

from core.data import (
    DataBase,
)


@users_bp.route("/register", methods=["POST"])
def register_user():
    """
    The function `register_user()` registers a new user by retrieving their email, email, and
    password from a form, checking if the email already exists in the database, creating a new User
    object with the provided information, and inserting the user into the database.

    Returns:
        - a string message indicating the result of the user registration process. If the email
    already exists in the database, it returns a message stating that the email already exists. If
    the registration is successful, it returns a message indicating that the user has been inserted and
    provides a link to the login page.
    """
    email = flask.request.form["email"]
    password = flask.request.form["password"]

    email = flask.request.form["email"]
    users, _ = DataBase().get_users_by_email(email=email)

    if len(users) != 0:
        return f"email {email} already exists!"

    print(password)
    user = UserModel(email=email, password_hash="unset", user_type="PROFESSOR")
    user.set_password(password=password)
    print(user.password_hash)
    DataBase().insert_user(user=user)
    return redirect("/login")
    return f'User {user} inserted, please <a href="/login">Login</a>'


@users_bp.route("/auth/google", methods=["POST"])
def oauth_register():
    user_info = request.json
    print(f"[OAUTH REGISTER] {user_info}")
    google_id = user_info.get("google_id")
    email = user_info.get("email")
    name = user_info.get("name")
    utype = user_info.get("utype")  # PROFESSOR | STUDENT
    redirect_from = user_info.get("redirect_from", None)
    picture = user_info.get("picture", "unset")

    if not google_id or not email or not name:
        return jsonify({"error": "Missing information from Google OAuth"}), 400

    # Register user if it doesn't exist
    users, _ = DataBase().get_users_by_email(email=email)

    if len(users) == 0:
        user = UserModel(
            email=email,
            password_hash="unset",
            user_type=utype,
            google_id=google_id,
            name=name,
            verified=True,
            picture=picture,
        )
        print(user)
        try:
            DataBase().insert_user(user)
            if redirect_from != None:
                print("[Enrolling]")
                c, s = DataBase().enroll_user_to_course_by_collectionname(
                    user.user_id, redirect_from
                )
                if c != None:
                    # aici
                    code_code = f"{uuid.uuid4()}"
                    user_access_code = AccessCodeModel(id=user.user_id, code=code_code, email=email)
                    DataBase().insert_access_code(user_access_code)
                    return (
                        jsonify(
                            {
                                "message": "User created",
                                "user": {
                                    "google_id": google_id,
                                    "email": email,
                                    "name": name,
                                    "picture": picture,
                                },
                                "redirect_to": c,
                                "sid": code_code,
                            }
                        ),
                        201,
                    )

            return (
                jsonify(
                    {
                        "message": "User created",
                        "user": {
                            "google_id": google_id,
                            "email": email,
                            "name": name,
                            "picture": picture,
                        },
                    }
                ),
                201,
            )
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    flask_login.login_user(users[0])
    DataBase().update_profile_pic(users[0].user_id, picture)
    if redirect_from != None:
        print("[Enrolling]")

        c, s = DataBase().enroll_user_to_course_by_collectionname(users[0].user_id, redirect_from)
        if c is not None:
            # aici
            # creezi keye
            code_code = f"{uuid.uuid4()}"
            user_access_code = AccessCodeModel(id=users[0].user_id, code=code_code, email=email)
            DataBase().insert_access_code(user_access_code)
            return (
                jsonify(
                    {
                        "message": "User logged in",
                        "user": {
                            "google_id": google_id,
                            "email": email,
                            "name": name,
                            "picture": picture,
                        },
                        "redirect_to": c,
                        "sid": code_code,
                    }
                ),
                201,
            )

    return (
        jsonify(
            {
                "message": "User logged in",
                "user": {"google_id": google_id, "email": email, "name": name, "picture": picture},
            }
        ),
        201,
    )


@users_bp.route("/login", methods=["POST"])
def login():
    """
    The login function checks if the email and password provided by the user match the stored
    email and password in the database, and logs the user in if they match.

    Returns:
        - The function `login()` returns either 'Invalid email', 'Bad login, <a
    href="/">Return</a>', or a redirect to "/protected" depending on the conditions met in the code.
    """
    email = flask.request.form["email"]
    users, _ = DataBase().get_users_by_email(email=email)
    if len(users) == 0:
        return "Invalid email"
    print("\n\nUser:")
    print(users[0])
    if users[0].verify_password(flask.request.form["password"]):
        flask_login.login_user(users[0])
        return flask.redirect("/")
    return 'Bad login, <a href="/">Return</a>'


@users_bp.route("/protected")
@flask_login.login_required
def protected():
    return redirect("/")


@users_bp.route("/logout")
def logout():
    """
    The function `logout` logs out the user and returns a message with a link to return to the homepage.
    Returns:
        - The string 'Logged out, <a href="/">Return</a>' is being returned.
    """
    flask_login.logout_user()
    return redirect("/")
    return 'Logged out, <a href="/">Return</a>'


@users_bp.route("/getuser", methods=["POST"])
@flask_login.login_required
def getuser():
    """
    The function `getuser` prints the email of the currently logged in user and returns it as a JSON
    object.
    Returns:
        - a JSON object containing the email of the currently logged in user.
    """
    print("Logged in as", flask_login.current_user.email)
    return jsonify({"email": flask_login.current_user.email})


@users_bp.route("/isloggedin", methods=["POST"])
def isloggedin():
    """
    The function checks if the current user is logged in and returns a JSON response indicating whether
    they are logged in or not.
    Returns:
        - The function isloggedin() returns a JSON object with a key-value pair indicating whether
    the user is logged in or not. If the current user is authenticated, it returns {'loggedin': True},
    otherwise it returns {'loggedin': False}.
    """
    print(
        "Is logged in: ",
        flask_login.current_user,
        flask_login.current_user.is_authenticated,
    )
    if flask_login.current_user.is_authenticated:
        print(flask_login.current_user)
        return jsonify(
            {
                "loggedin": True,
                "verified": flask_login.current_user.verified == "true",
                "user": flask_login.current_user.jsonserialize(),
            }
        )
    return jsonify({"loggedin": False, "verified": False})


@users_bp.route("/users/<email>/mycourses", methods=["POST"])
@flask_login.login_required
def getusercourses(email):
    """
    The function `getusercourses` retrieves the courses associated with a given email and returns
    them in JSON format.
    URLParams:
        ```
        {
            "email" : str #  the email of the user for whom you want to retrieve
    the courses
        }
        ```
    Returns:
        - a JSON response containing the courses associated with the given email.

        ```
        {
            "courses" : list[CourseModel]
        }
        ```
    """
    if email != flask_login.current_user.email:
        return 'Not allowed, <a href="/">Return</a>'
    courses, _ = DataBase().get_user_by_email_courses(email=email)
    arr = [c.jsonserialize() for c in courses]
    return jsonify({"courses": arr})


@users_bp.route("/users/<email>/courses/<course>", methods=["POST"])
@flask_login.login_required
def getusercoursessections(email, course):
    """
    The function `getusercoursessections` returns the sections of a given course for a specific user,
    but only if the email matches the currently logged in user.

    Args:
        email (str): The `email` parameter is the email of the user for whom we want to retrieve
    the courses and sections. It is used to check if the user is authorized to access the information

        course (str): The "course" parameter is the ID or name of the course for which you want to retrieve
    the sections

    Returns:
        - a JSON object containing the sections of a specific course.

        ```
        {
            "sections": list[{
                "section_id": section.section_id,
                "course_id": course_id,
                "section_url": section.sectionurl,
                "pullingfrom": section.pulling_from,
                "course_chroma_collection": collection name,
            }] # sections in old format
        }
        ```
    """
    if email != flask_login.current_user.email:
        return 'Not allowed, <a href="/">Return</a>'
    sections, _ = DataBase().get_courses_sections_format(course_id=course)
    students, _ = DataBase().get_courses_students(course_id=course)
    messages, _ = DataBase().get_course_messages_2(course_id=course)

    print("MAIN FUNC")
    print(messages)
    # messages, _ = DataBase().get_mes
    return jsonify({"sections": sections, "students": students, "messages": messages})


@users_bp.route("/users/<email>/courses/<course>/<uid>", methods=["POST"])
@flask_login.login_required
def getusercoursessections_byuid(email, course, uid):
    """
    TODO: comment
    """
    if email != flask_login.current_user.email:
        return 'Not allowed, <a href="/">Return</a>'
    messages, _ = DataBase().get_course_messages_by_user(course_id=course, user_id=uid)
    print("MAIN FUNC")
    print(messages)
    # messages, _ = DataBase().get_mes
    return jsonify({"messages": messages})


@users_bp.route("/users/<email>/coursesv1/<course>", methods=["POST"])
@flask_login.login_required
def getusercoursessectionsv1(email, course):
    """
    The function `getusercoursessectionsv1` returns the sections of a given course for a specific user,
    but only if the user is currently logged in.

    Args:
        email (str): The `email` parameter is the email of the user for whom we want to retrieve
    the courses and sections. It is used to check if the user is authorized to access the information

        course (str): The "course" parameter is the ID or name of the course for which you want to retrieve
    the sections

    Returns:
        - a JSON object containing the sections of a specific course.

        ```
        {
            "sections": list[SectionModel] # sections in new format
        }
        ```
    """
    if email != flask_login.current_user.email:
        return 'Not allowed, <a href="/">Return</a>'
    sections, _ = DataBase().get_courses_sections(course_id=course)
    return jsonify({"sections": sections})


@users_bp.route("/student/register", methods=["POST"])
def student_register():
    """
    The function `student_register` registers a new student user by retrieving the email, email, and
    password from a form, checking if the email already exists, creating a new User object with the
    provided information, and inserting the user into the message database.

    Returns:
    - a string message indicating the result of the user registration process. If the email
    already exists in the database, it returns a message stating that the email already exists. If
    the registration is successful, it returns a message indicating that the user has been inserted and
    provides a link to the login page.
    """
    email = flask.request.form["email"]
    password = flask.request.form["password"]

    email = flask.request.form["email"]
    users, _ = DataBase().get_users_by_email(email=email)

    if len(users) != 0:
        return f"email {email} already exists!"

    print(password)
    user = UserModel(email=email, password_hash="unset", user_type="STUDENT")
    user.password = password
    print(user.password_hash)
    DataBase().insert_user(user=user)
    return f'User {user} inserted, please <a href="/login">Login</a>'


@users_bp.route("/users/send_verification_mail", methods=["POST", "GET"])
def user_send_mail():
    current_user = flask_login.current_user

    code, ok = EmailSender().send(current_user)
    if ok:
        return jsonify({"code": code, "user_id": current_user.user_id})
    else:
        # return "Error! <a href='/users/send_verification_mail'> Try again! </a>"
        return jsonify(
            {"error": 1, "message": "Could not send mail!", "user_id": current_user.user_id}
        )


@users_bp.route("/users/verify/<code>", methods=["POST", "GET"])
def user_verify(code):
    current_user = flask_login.current_user

    res, _ = DataBase().get_verif(code)
    if not res or (res.user_id != current_user.user_id):
        return "Something went wrong <a href='/'>Go home and try again!</a>"
    else:
        DataBase().verify_user(current_user.user_id)
        return "User verified! <a href='/'>Go home!</a>"


@users_bp.route("/users/forgotpassword", methods=["POST", "GET"])
def user_forgotpassword():
    new_password = flask.request.form["new_password"]
    code = flask.request.form["code"]
    email = flask.request.form["emaila"]
    res, _ = DataBase().get_reset_code(email, code)
    if not res or res.code != code:
        return f"Something went wrong <a href='/'>Go home and try again! {res.code}</a>"
    else:

        ok, session = DataBase().reset_user_password(new_password, code=code)

        if ok is None:
            return "Error: User password NOT reset! <a href='/'>Go home!</a>"
        else:
            return "User password reset! <a href='/'>Go home!</a>"


@users_bp.route("/users/sendresetemail", methods=["POST", "GET"])
def forgot_password_send():
    email = flask.request.form["email"]
    code, ok = EmailSender().send_forgot_password(email)
    if ok:
        return jsonify({"code": code})
    else:
        # return "Error! <a href='/users/send_verification_mail'> Try again! </a>"
        return jsonify({"error": 1, "message": "Could not send mail!"})
