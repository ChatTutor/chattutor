import json
import os

with open('./keys.json') as f:
    keys = json.load(f)
os.environ['OPENAI_API_KEY'] = keys["lab_openai"]
os.environ['ACTIVELOOP_TOKEN'] = keys["activeloop"]

from flask import Flask, request, redirect, send_from_directory, url_for
from flask_cors import CORS
from extensions import db
import tutor

app = Flask(__name__)
CORS(app)
db.init_db()

@app.route("/")
def index():
    return redirect(url_for('static', filename='index.html'))

@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

@app.route("/ask", methods=["POST", "GET"])
def ask():
    data = request.json
    conversation = data["conversation"]
    collection_name = data["collection"]
    from_doc = data.get("from_doc")

    if(from_doc): print("only from doc", from_doc)
    else: print("from any doc")

    db.load_datasource(collection_name)
    response = tutor.ask_question(db, conversation, from_doc)
    return response

if __name__ == "__main__":
    app.run(debug=False)