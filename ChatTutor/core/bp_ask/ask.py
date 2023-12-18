import flask
from flask import (
    Flask,
    request,
    redirect,
    send_from_directory,
    url_for,
    render_template,
)
from flask import stream_with_context, Response, abort, jsonify
from flask_cors import CORS
from itsdangerous import URLSafeTimedSerializer
from flask import Blueprint, render_template
from core.tutor import Tutor
from core.tutor import (
    cqn_system_message,
    default_system_message,
    interpreter_system_message,
)
import json
from nice_functions import pprint, time_it
from core.extensions import (
    db,
    user_db,
    messageDatabase,
    get_random_string,
    generate_unique_name,
    stream_text,
)

ask_bp = Blueprint("bp_ask", __name__)


@ask_bp.route("/", methods=["POST", "GET"])
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
    collection_name = data.get("collection")
    collection_desc = data.get("description")
    multiple = data.get("multiple")
    from_doc = data.get("from_doc")
    selected_model = data.get("selectedModel")
    if selected_model == None:
        selected_model = "gpt-3.5-turbo-16k"
    print("SELECTED MODEL:", selected_model)
    print(collection_name)
    # Logging whether the request is specific to a document or can be from any document
    chattutor = Tutor(db)
    if collection_name and collection_name != []:
        if multiple == None:
            name = collection_desc if collection_desc else ""
            chattutor.add_collection(collection_name, name)
        else:
            chattutor = Tutor(db, system_message=default_system_message)
            if "test_embedding" in collection_name:
                chattutor = Tutor(db, system_message=cqn_system_message)
            for cname in collection_name:
                message = (
                    f"CQN papers "
                    if cname == "test_embedding"
                    else """Use the following user uploaded files to provide information if asked about content from them. 
                User uploaded files """
                )
                chattutor.add_collection(cname, message)

    generate = chattutor.stream_response_generator(
        conversation, from_doc, selected_model
    )
    return Response(stream_with_context(generate()), content_type="text/event-stream")


@ask_bp.route("/interpreter", methods=["POST", "GET"])
def ask_interpreter():
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
    collection_name = data.get("collection")
    collection_desc = data.get("description")
    multiple = data.get("multiple")
    from_doc = data.get("from_doc")
    selected_model = data.get("selectedModel")
    if selected_model == None:
        # selected_model = 'gpt-3.5-turbo-16k'
        selected_model = "gpt-4"
    print("SELECTED MODEL:", selected_model)
    print(collection_name)
    # Logging whether the request is specific to a document or can be from any document
    chattutor = Tutor(db)
    if collection_name:
        if multiple == None:
            name = collection_desc if collection_desc else ""
            chattutor.add_collection(collection_name, name)
        else:
            chattutor = Tutor(db, system_message=interpreter_system_message)
            for cname in collection_name:
                message = (
                    f"CQN papers "
                    if cname == "test_embedding"
                    else """Use the following user uploaded files to provide information if asked about content from them. 
                User uploaded files """
                )
                chattutor.add_collection(cname, message)
    generate = chattutor.stream_interpreter_response_generator(
        conversation, from_doc, selected_model
    )
    return stream_with_context(generate())
