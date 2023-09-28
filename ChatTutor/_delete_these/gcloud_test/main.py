from flask import Flask, Response, request, session, render_template, redirect, jsonify
from flask_session import Session

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route("/")
def index():
    return "home"

@app.route("/ask", methods=["GET"])
def ask():
    if not session.get("counter"):
        session["counter"] = 1
    else: session["counter"] += 1
    return "ask endpoint"

@app.route("/history", methods=["GET"])
def history():
    if not session.get("counter"):
        return "Counter: 0"
    return f"Counter: {session.get('counter')}"

@app.route("/reset", methods=["GET", "POST"])
def reset():
    return "reset endpoint"

if __name__ == "__main__":
    app.run(debug=False)