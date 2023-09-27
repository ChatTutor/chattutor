from flask import Flask, request, redirect, send_from_directory, url_for
from flask import stream_with_context, Response
from flask_cors import CORS  # Importing CORS to handle Cross-Origin Resource Sharing
from extensions import db  # Importing the database object from extensions module
import tutor
import json
import time
import os
#import openai

with open('./keys.json') as f:
    keys = json.load(f)
os.environ['OPENAI_API_KEY'] = keys["lab_openai"]
os.environ['ACTIVELOOP_TOKEN'] = keys["activeloop"]
#openai.api_key = keys["lab_openai"]
app = Flask(__name__)
CORS(app)  # Enabling CORS for the Flask app to allow requests from different origins
db.init_db()

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
        start_time = time.time()
        for chunk in tutor.ask_question(db, conversation, from_doc):
            chunk_time = time.time() - start_time
            yield f"data: {json.dumps({'time': chunk_time, 'message': chunk})}\n\n"
    
    # Streaming the generated responses as server-sent events
    return Response(stream_with_context(generate()), content_type='text/event-stream')

if __name__ == "__main__":
    app.run(debug=False)  # Running the app in release mode
