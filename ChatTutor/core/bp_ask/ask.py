
from core.extensions import (db)
from flask import (Blueprint, Response, request, stream_with_context)
from core.tutor.tutorfactory import TutorFactory, TutorTypes
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
    multiple = data.get("multiple")

    conversation = data["conversation"]
    collection_name = data.get("collection")
    collection_desc = data.get("description")
    response_type = data.get("response_type", "COURSE_RESTRICTED")
    from_doc = data.get("from_doc")
    selected_model = data.get("selectedModel", "gpt-3.5-turbo-16k")
    
    tutor_type = TutorTypes.from_string(response_type)
    
    # Logging whether the request is specific to a document or can be from any document
    # todo: get bot type from token
    print("SELECTED MODEL:", selected_model)
    print(collection_name)
    _chattutor = tutorfactory.build_empty(tutor_type)
    if collection_name != None and collection_name != []:
        _chattutor = tutorfactory.build(tutor_type, collection_name, collection_desc)
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
    response_type = data.get("response_type", "COURSE_RESTRICTED")

    from_doc = data.get("from_doc")
    selected_model = data.get("selectedModel", "gpt-4")
    tutor_type = TutorTypes.from_string(response_type)
    
    # Logging whether the request is specific to a document or can be from any document
    print("SELECTED MODEL:", selected_model)
    print(collection_name)
    
    _chattutor = tutorfactory.build(tutor_type, collection_name, collection_desc)
    generate = _chattutor.stream_interpreter_response_generator(
        conversation, from_doc, selected_model
    )
    return stream_with_context(generate())
