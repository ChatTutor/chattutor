import uuid

import flask
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


def connect_to_database():
    """Function that connects to the database"""
    # for mysql server
    # connection = pymysql.connect(
    #     host='localhost',
    #     user='root',
    #     password='password',
    #     db='mydatabase',
    #     charset='utf8mb4',
    #     cursorclass=pymysql.cursors.DictCursor
    # )
    # return connection
    return sqlite3.connect('chat_store.sqlite3')


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

@app.route('/getfromdb', methods=["POST", "GET"])
def getfromdb():
    data = request.form
    username = data.get('lusername', 'nan')
    passcode = data.get('lpassword', 'nan')
    print(data)
    print(username, passcode)
    if username == 'root' and passcode == 'admin':
        with connect_to_database() as con:
            cur = con.cursor()
            response = cur.execute('SELECT * FROM lmessages JOIN lchats ON lmessages.chat_key = lchats.chat_id')
            messages_arr = response.fetchall()
            renderedString = ""
            for message in messages_arr:
                role = message[1]
                content = message[2]
                chat_id = message[3]
                msg_html = f"""
                    <div class="left-msg">
                        <div class="msg-bgd">
                          <div class="msg-bubble">
                            <div class="msg-info">
                              <div class="msg-info-name">role: {role}</div>
                              <div class="msg-info-name">chat_key: {chat_id}</div>
                            </div>

                            <div class="msg-text">content: {content}</div>
                          </div>
                        </div>
                    </div>
                """
                renderedString += msg_html

            return flask.render_template('display_messages.html', renderedString=renderedString)
    else:
        return flask.render_template_string('Error, please <a href="/static/display_db.html">Go back</a>')


@app.route('/exesql', methods=["POST", "GET"])
def exesql():
    data = request.json
    username = data['lusername']
    passcode = data['lpassword']
    sqlexec = data['lexesql']
    if username == 'root' and passcode == 'admin':
        with connect_to_database() as con:
            cur = con.cursor()
            response = cur.execute(sqlexec)
            messages_arr = response.fetchall()
            return Response(f'{messages_arr}', 200)
    else:
        return Response('fail', 404)

def print_for_debug():
    """For debugging purposes. Acceses  the content of the lmessages table"""
    with connect_to_database() as con:
        cur = con.cursor()
        # This accesses the contents in the database ( for messages )
        response = cur.execute('SELECT * from lmessages')
        # response = cur.execute('SELECT * from lchats') -- this is for chats.
        print("DC:", response.fetchall())



def insert_message(a_message):
    """This inserts a message into the sqlite3 database."""
    with connect_to_database() as con:
        cur = con.cursor()
        insert_format_lmessages = "INSERT INTO lmessages (role, content, chat_key) VALUES (?, ?, ?)"
        role = a_message['role']
        content = a_message['content']
        chat_key = a_message['chat']
        cur.execute(insert_format_lmessages, (role, content, chat_key))



def insert_chat(chat_key):
    """This inserts a chat into the sqlite3 database, ignoring the command if the chat already exists."""
    with connect_to_database() as con:
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
