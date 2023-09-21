from flask import Flask, Response, request, session, render_template, redirect, jsonify, url_for
from flask_login import LoginManager, login_user, current_user, login_required, UserMixin, logout_user
from flask_cors import CORS
from flask_session import Session

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'qpoeriuqewporiualdkfjad'
login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)

class User(UserMixin):
    id=5
    name = "Joe"

@app.route("/index")
def index():
    return "Hello"

@app.route("/login", methods=["POST", "GET"])
def login():
    login_user(User(), False)
    return redirect(url_for('index'))

@app.route("/profile", methods=["GET"])
@login_required
def profile():
    return current_user.name

@app.route("/reset", methods=["GET", "POST"])
def reset():
    return "another random page"

@login_manager.user_loader
def load_user(user_id):
    # since the user_id is just the primary key of our user table, use it in the query for the user
    return User()

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=False)