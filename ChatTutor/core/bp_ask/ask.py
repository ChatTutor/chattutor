
from core.extensions import (db)
from flask import (Blueprint, Response, request, stream_with_context)
from core.tutor.tutorfactory import TutorFactory
from core.tutor.tutorfactory import CourseTutorType, NSFTutorType
from core.tutor.systemmsg import (cqn_system_message, default_system_message,
                        interpreter_system_message)
tutorfactory = TutorFactory(db)
ask_bp = Blueprint("bp_ask", __name__)


@ask_bp.route("", methods=["POST", "GET"])
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
    # todo: get bot type from token
    _chattutor = tutorfactory.build_empty(CourseTutorType.COURSE_RESTRICTED)
    if collection_name != None and collection_name != []:
        _chattutor = tutorfactory.build(CourseTutorType.COURSE_FOCUSED, collection_name, collection_desc)
    generate = _chattutor.stream_response_generator(
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
    _chattutor = tutorfactory.build(CourseTutorType.COURSE_RESTRICTED, collection_name, collection_desc)
    generate = _chattutor.stream_interpreter_response_generator(
        conversation, from_doc, selected_model
    )
    return stream_with_context(generate())
