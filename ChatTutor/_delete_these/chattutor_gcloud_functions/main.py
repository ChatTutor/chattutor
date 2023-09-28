import json
import os
import functions_framework
from database import VectorDatabase
import tutor
import openai

@functions_framework.http
def ask(request):
    # Set CORS headers for the preflight request
    if request.method == "OPTIONS":
        headers = {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET",
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Max-Age": "3600",
        }

        return ("", 204, headers)

    data = request.get_json(silent=True)
    conversation = data["conversation"]
    collection_name = data["collection"]
    from_doc = data.get("from_doc")

    with open('./keys.json') as f:
        keys = json.load(f)
        openai.api_key = keys["lab_openai"]

    db = VectorDatabase("./db", 'deeplake_tensordb')
    db.load_datasource(collection_name)
    response = tutor.ask_question(db, conversation, from_doc)

    headers = {"Access-Control-Allow-Origin": "*"}
    return (response, 200, headers)