import uuid

from flask import Flask, request, redirect, send_from_directory, url_for
from flask import stream_with_context, Response, abort
from flask_cors import CORS  # Importing CORS to handle Cross-Origin Resource Sharing
from extensions import db  # Importing the database object from extensions module
import tutor
import json
import time
import os
# import pymysql
import sqlite3
import openai
import loader


if 'CHATUTOR_GCP' in os.environ: 
    openai.api_key = os.environ['OPENAI_API_KEY']
else:
    import yaml
    with open('.env.yaml') as f:
        yamlenv = yaml.safe_load(f)
    keys = yamlenv["env_variables"]
    print(keys)
    os.environ['OPENAI_API_KEY'] = keys["OPENAI_API_KEY"]
    os.environ['ACTIVELOOP_TOKEN'] = keys["ACTIVELOOP_TOKEN"]

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
# ) ## for mysql server TO BE USED INSTEAD OF 'con'.

# Only for deleting the db when you first access the site. Can be used for debugging
presetTables1 = """
    DROP TABLE IF EXISTS lchats
"""
# only for deleting the db when you first access the site. Can be used for debugging
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
    FOREIGN KEY (chat_key) REFERENCES lchats (chat_id)
    )"""


def initialize_ldatabase():
    """Creates the tables if they don't exist"""
    con = sqlite3.connect('chat_store.sqlite3')
    cur = con.cursor()
    #if you want to delete the database when a user acceses the site. (For DEBUGGING purposes only
    # cur.execute(presetTables1)
    # cur.execute(presetTables2)
    cur.execute(chats_table_Sql)
    cur.execute(messages_table_Sql)

initialize_ldatabase()

@app.route("/")
def index():
    """
        Serves the landing page of the web application which provides
        the ChatTutor interface. Users can ask the Tutor questions and it will
        response with information from its database of papers and information.
        Redirects the root URL to the index.html in the static folder
    """
    return redirect(url_for('static', filename='index.html'))

@app.route('/static/<path:path>')
def serve_static(path):
    """Serving static files from the 'static' directory"""
    return send_from_directory('static', path)

@app.route("/ask", methods=["POST", "GET"])
def ask():
    """Route that facilitates the asking of questions. The response is generated
    based on an embedding.
    
    URLParams:
        conversation (List({role: ... , content: ...})):  snapshot of the current conversation 
        collection: embedding used for vectorization
    Yields:
        response: {data: {time: ..., message: ...}}
    """
    data = request.json
    conversation = data["conversation"]
    collection_name = data["collection"]
    from_doc = data.get("from_doc")
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
    print_for_debug()
    return Response('inserted!', content_type='text')


def print_for_debug():
    """For debugging purposes. Acceses  the content of the lmessages table"""
    with sqlite3.connect('chat_store.sqlite3') as con:
        cur = con.cursor()
        # This accesses the contents in the database ( for messages )
        response = cur.execute('SELECT * from lmessages')
        # response = cur.execute('SELECT * from lchats') -- this is for chats.
        print("DC:", response.fetchall())


def insert_message(a_message):
    """This inserts a message into the sqlite3 database."""
    with sqlite3.connect('chat_store.sqlite3') as con:
        cur = con.cursor()
        insert_format_lmessages = "INSERT INTO lmessages (role, content, chat_key) VALUES (?, ?, ?)"
        role = a_message['role']
        content = a_message['content']
        chat_key = a_message['chat']
        cur.execute(insert_format_lmessages, (role, content, chat_key))



def insert_chat(chat_key):
    """This inserts a chat into the sqlite3 database, ignoring the command if the chat already exists."""
    with sqlite3.connect('chat_store.sqlite3') as con:
        cur = con.cursor()
        insert_format_lchats = "INSERT OR IGNORE INTO lchats (chat_id) VALUES (?)"
        cur.execute(insert_format_lchats, (chat_key,))

@app.route('/compile_chroma_db', methods=['POST'])
def compile_chroma_db():
    token = request.headers.get('Authorization')

    if token != openai.api_key:
        abort(401)  # Unauthorized
    
    loader.init_chroma_db()

    return "Chroma db created successfully", 200

if __name__ == "__main__":
    app.run(debug=True)  # Running the app in debug mode
