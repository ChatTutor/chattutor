import flask
from flask import Flask, request, redirect, send_from_directory, url_for
from flask import stream_with_context, Response, abort
from flask_cors import CORS  # Importing CORS to handle Cross-Origin Resource Sharing
from extensions import db  # Importing the database object from extensions module
import tutor
import json
import time
import os
import openai
import loader
from messagedb import MessageDB

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

messageDatabase = MessageDB(host='34.41.31.71',
                            user='admin',
                            password='AltaParolaPuternica1245',
                            database='chatmsg',
                            statistics_database='sessiondat')


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
    if (from_doc):
        print("only from doc", from_doc)
    else:
        print("from any doc")

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
    clear_number = data['clear_number']
    time_created = data['time_created']
    messageDatabase.insert_chat(chat_k_id)
    message_to_upload = {'content': content, 'role': role, 'chat': chat_k_id, 'clear_number': clear_number,
                         'time_created': time_created}
    messageDatabase.insert_message(message_to_upload)
    return Response('inserted!', content_type='text')


@app.route('/getfromdb', methods=["POST", "GET"])
def getfromdb():
    data = request.form
    username = data.get('lusername', 'nan')
    passcode = data.get('lpassword', 'nan')
    print(data)
    print(username, passcode)
    if username == 'root' and passcode == 'admin':
        messages_arr = messageDatabase.execute_sql(
            "SELECT * FROM lmessages ORDER BY chat_key, clear_number, time_created", True)
        renderedString = messageDatabase.parse_messages(messages_arr)
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
        messages_arr = messageDatabase.execute_sql(sqlexec)
        return Response(f'{messages_arr}', 200)
    else:
        return Response('wrong password', 404)


@app.route('/compile_chroma_db', methods=['POST'])
def compile_chroma_db():
    token = request.headers.get('Authorization')

    if token != openai.api_key:
        abort(401)  # Unauthorized

    loader.init_chroma_db()

    return "Chroma db created successfully", 200


if __name__ == "__main__":
    app.run(debug=True)  # Running the app in debug mode
