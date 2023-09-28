import uuid

from flask import Flask, request, redirect, send_from_directory, url_for
from flask import stream_with_context, Response
from flask_cors import CORS  # Importing CORS to handle Cross-Origin Resource Sharing
from extensions import db  # Importing the database object from extensions module
import tutor
import json
import time
import os
# import pymysql
import sqlite3

with open('./keys.json') as f:
    keys = json.load(f)
os.environ['OPENAI_API_KEY'] = keys["lab_openai"]
#os.environ['ACTIVELOOP_TOKEN'] = keys["activeloop"]

app = Flask(__name__)
CORS(app)  # Enabling CORS for the Flask app to allow requests from different origins
db.init_db()

# connection = pymysql.connect(
#     host='localhost',
#     user='root',
#     password='password',
#     db='mydatabase',
#     charset='utf8mb4',
#     cursorclass=pymysql.cursors.DictCursor
# ) ## for mysql server


presetTables1 = """
    DROP TABLE IF EXISTS lchats
"""

presetTables2 = """
    DROP TABLE IF EXISTS lmessages
"""

chats_table_Sql = """
CREATE TABLE IF NOT EXISTS lchats (
    chat_id text PRIMARY KEY
    )"""

messages_table_Sql = """
CREATE TABLE IF NOT EXISTS lmessages (
    mes_id text PRIMARY KEY,
    role text NOT NULL,
    content text NOT NULL,
    chat_key integer NOT NULL,
    FOREIGN KEY (chat_key) REFERENCES chats (chat_id)
    )"""


def initialize_ldatabase():
    con = sqlite3.connect('chat_store.sqlite3')
    cur = con.cursor()
    # cur.execute(presetTables1)
    # cur.execute(presetTables2)
    cur.execute(chats_table_Sql)
    cur.execute(messages_table_Sql)

initialize_ldatabase()

@app.route("/")
def index():
    # Redirecting the root URL to the index.html in the static folder
    return redirect(url_for('static', filename='index.html'))

@app.route('/static/<path:path>')
def serve_static(path):
    # Serving static files from the 'static' directory
    return send_from_directory('static', path)

@app.route("/ask", methods=["POST", "GET"])
def ask():
    data = request.json
    conversation = data["conversation"]
    collection_name = data["collection"]
    from_doc = data.get("from_doc")

    # print("convo: ", data['conversation'])

    # Logging whether the request is specific to a document or can be from any document
    if(from_doc): print("only from doc", from_doc)
    else: print("from any doc")

    db.load_datasource(collection_name)

    def generate():
        # This function generates responses to the questions in real-time and yields the response
        # along with the time taken to generate it.
        chunks = ""
        start_time = time.time()
        for chunk in tutor.ask_question(db, conversation, from_doc):
            chunk_content = ""
            if 'content' in chunk:
                chunk_content = chunk['content']
            chunks += chunk_content
            chunk_time = time.time() - start_time
            yield f"data: {json.dumps({'time': chunk_time, 'message': chunk})}\n\n"
    return Response(stream_with_context(generate()), content_type='text/event-stream')

@app.route('/addtodb', methods=["POST", "GET"])
def addtodb():
    data = request.json
    content = data['content']
    role = data['role']
    chat_k_id = data['chat_k']
    insert_chat(chat_k_id)
    message_to_upload = {'content': content, 'role': role, 'chat': chat_k_id}
    insert_message(message_to_upload)
    print('HEY: ', message_to_upload)
    print_for_debug()
    return Response('inserted!', content_type='text')

def print_for_debug():
    with sqlite3.connect('chat_store.sqlite3') as con:
        cur = con.cursor()
        response = cur.execute('SELECT * from lmessages')
        print(response.fetchall())

def insert_message(a_message):
    with sqlite3.connect('chat_store.sqlite3') as con:
        cur = con.cursor()
        insert_format_lmessages = "INSERT INTO lmessages (role, content, chat_key) VALUES (?, ?, ?)"
        role = a_message['role']
        content = a_message['content']
        chat_key = a_message['chat']
        cur.execute(insert_format_lmessages, (role, content, chat_key))

def insert_chat(chat_key):
    with sqlite3.connect('chat_store.sqlite3') as con:
        cur = con.cursor()
        insert_format_lchats = "INSERT OR IGNORE INTO lchats (chat_id) VALUES (?)"
        cur.execute(insert_format_lchats, (chat_key,))



if __name__ == "__main__":
    app.run(debug=True)  # Running the app in debug mode
