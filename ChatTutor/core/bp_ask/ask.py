
from core.extensions import (db)
from core.tutor import (Tutor, cqn_system_message, default_system_message,
                        interpreter_system_message)
from flask import (Blueprint, Response, request, stream_with_context)
from typing import Iterator

ask_bp = Blueprint("bp_ask", __name__)


@ask_bp.route("", methods=["POST", "GET"])
def ask() -> Response:
    """Route that facilitates the asking of questions. The response is generated
    based on an embedding.

    URLParams:
        conversation (List({role: ... , content: ...})):  snapshot of the current conversation
        collection: embedding used for vectorization
    Yields:
        response: {data: {time: ..., message: ...}}
    """
    data = request.json

    # get credentials
    credential_user = data.get("credential_token")
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
def ask_interpreter() -> Iterator:
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
