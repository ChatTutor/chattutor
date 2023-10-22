from copy import deepcopy
from pprint import pp
import sys 
sys.path.insert(0, ".")

import pathlib
from utils.hash import get_hash
from nice_functions import *
from os.path import join
import os
from nice_functions import *
import tiktoken

from core.extensions import db
from core.openai_tools import load_api_keys
import openai

def print_summary_medium():
    load_api_keys()
    db.init_db()
    db.load_datasource("test_embedding_medium")
    docs = db.datasource.get(limit=10)
    pprint(docs)
    
def print_summary_basic():
    load_api_keys()
    db.init_db()
    db.load_datasource("test_embedding_basic")
    docs = db.datasource.get(limit=10)
    pprint(docs)

   

def simple_gpt(system_message, user_message):
    models_to_try = ["gpt-3.5-turbo-16k", "gpt-3.5-turbo"]
    for model_to_try in models_to_try:
        try:
            response = openai.ChatCompletion.create(
                model=model_to_try,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message},
                ],
                temperature=1,
                frequency_penalty=0.0,
                presence_penalty=0.0,
                # stream=True,
            )
            return response.choices[0].message.content
        except Exception as e:
            print(red(model_to_try), "FAILED!")
            if model_to_try == models_to_try[-1]: raise(e)


def reduce_synopsis(synopsis, to_number_of_tokens):
    answer = simple_gpt(
        "You are a bot capable of summarize scientific articles", 
        rf"Please, can you summarize the following text returning no more than {to_number_of_tokens} tokens? The text to summarize is: {synopsis}")
    return answer

def create_pdf_summary():
    load_api_keys()
    db.init_db()

    offset = 0
    limit = 1000
    while True:
        print(f"Getting documents {offset} to {offset+limit} ...")

        
        db.load_datasource("test_embedding")
        docs_full = db.datasource.get( offset=offset, limit=limit, include=["metadatas"])
        if docs_full["ids"] == []: break
        offset+=limit
        
        summary_keys = [{
            "name": "Paper Title",
            "regex": "title"
        },{
            "name": "Paper Authors",
            "regex": "author",
        },{
            "name": "Paper Published Data",
            "regex": "published"
        },{
            "name": "Paper Link",
            "regex": "links"
        },{
            "name": "Paper Summary",
            "regex": "summary"        
        }]
        
        keys_for_uid = ["Paper Title", "Paper Authors", "Paper Published Data"]
        
        docs_summarized = {}
        docs_metadatas = {}
        for doc_metadata in docs_full["metadatas"]:
            doc_summarized = get_doc_summary(doc_metadata, summary_keys)
            if doc_summarized=={}:continue
            str_for_id = [v for k, v in doc_summarized.items() if k in keys_for_uid]
            uid = get_hash(str_for_id)
            docs_summarized[uid] = doc_summarized
            docs_metadatas[uid] = doc_metadata
        
        pprint("Total documents:", len(docs_summarized))
        levels = ["medium", "basic"]
        
        for level in levels: 
            print()
            print(f"Generating {level} level resumen")
            db.load_datasource(rf"test_embedding_{level}")
            current_uids = db.datasource.get(include=[])["ids"]

            for uid, _doc_summarized in docs_summarized.items():
                doc_summarized = deepcopy(_doc_summarized)
                if uid in current_uids:
                    print(f"{green(uid)}: {doc_summarized['Paper Title'][0:50]}\n -> {blue('already added')}")
                    continue
                
                if level == "medium":
                    synopsis = doc_summarized.get("Paper Summary", "")
                    synopsis_tokens = len(tiktoken.get_encoding("cl100k_base").encode(synopsis))
                    if synopsis_tokens > 300:
                        print("Summary too loog... reducing...")
                        synopsis = reduce_synopsis(synopsis, to_number_of_tokens=300)
                        doc_summarized["Paper Summary"] = synopsis
                elif level == "basic":
                    doc_summarized.pop("Paper Summary")

                summarized_docs_string = stringify_doc_summary(doc_summarized)
                doc_metadata = docs_metadatas[uid]
                db.datasource.add(
                    ids=uid,
                    metadatas=doc_metadata,
                    documents=summarized_docs_string,
                )
                print(f"{green(uid)}: {doc_summarized['Paper Title'][0:50]}\n -> {green('added')}")

def get_content_cache_file_name(datasource_name):
    cache_folder = get_cache_folder()
    safe_name = get_hash(datasource_name)
    file_name = join(cache_folder, safe_name)
    return file_name

def read_content_from_cache(datasource_name):
    file_name = get_content_cache_file_name(datasource_name)
    
    if not os.path.exists(file_name):
        raise(Exception(f"cached content does not exist. generate it by running {blue('/test_scripts/generate_cache_content.py')}"))
    
    with open(file_name) as f:
        contents = f.readlines()
    return "".join(contents)    

def save_content_to_cache(content, datasource_name):
    cache_file_name = get_content_cache_file_name(datasource_name)
    f = open(cache_file_name, "a")
    f.write(content)
    f.close()

def get_cache_folder():
    return pathlib.Path(__file__).parent


def get_keys_by_regex(regex, dict):
    keys = []
    import re
    for k,v in dict.items():
        if re.findall(regex, k, flags=re.IGNORECASE):
            keys.append(k)
    return keys
    
def get_doc_summary(doc_metadata, summary_keys):
    doc_summary = {}
    for summary_key in summary_keys:
        summary_key_name = summary_key["name"]
        summary_key_regex = summary_key["regex"]
        summary_key_function = summary_key.get("function", None)
        doc_metadata_keys = get_keys_by_regex(summary_key_regex, doc_metadata)
        if doc_metadata_keys:
            summary_key_value = get_values_from_keys(doc_metadata_keys, doc_metadata)
            if not summary_key_value: continue
            if summary_key_function == None:
                doc_summary[summary_key_name] = summary_key_value
            else:
                raise(Exception("To be implemented"))      
    return doc_summary
                        
def stringify_doc_summary(doc_summary):
    doc_summary_str = ""
    for k, v in doc_summary.items():
        if v: doc_summary_str+=f"{k}: {v}\n"
    return doc_summary_str

def get_values_from_keys(keys, dict, joiner = ", "):
    return joiner.join([ v for k,v in dict.items() if k in keys ])

