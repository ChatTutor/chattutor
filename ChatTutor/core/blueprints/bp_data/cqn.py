from multiprocessing import JoinableQueue, Pool, Process, Queue
import time

# import pymysql
## search for TODO : modify
import io
import json
from typing import List

import PyPDF2
import flask
import os

import pdfreader

# import markdown
import flask_login
import requests

from core.extensions import db
from flask import Blueprint, Response, jsonify, request
from datetime import datetime
from core.data import (
    DataBase,
    UserModel,
    MessageModel,
    FeedbackModel,
    SectionModel,
    CourseModel,
    ChatModel,
)
from scholarly import scholarly, Author, Publication
from google_scholar_py import *
from core.reader import parse_pdf, Text, Doc
import multiprocessing


def run_with_timeout(func, timeout, *args, **kwargs):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(func, *args, **kwargs)
        try:
            result = future.result(timeout=timeout)
            return result
        except concurrent.futures.TimeoutError:
            print("[TIMEOUT] on function")
            return None


class CQNPublications:
    title: str
    snippet: str
    link: str
    resources: List
    authors: List
    pdf_contents: List[Text] = []

    def set_pdf_contents(self, content_url, i):
        doc = Doc(docname=f"{content_url}", citation="", dockey=f"{content_url}")

        texts = []
        content_url = content_url.replace("html", "pdf")
        resp = requests.get(content_url)
        print(f"\n\n{content_url}:\n")
        open_pdf_file = resp.content
        print(f"\n\tGettng texts {i}\n")
        texts = parse_pdf(open_pdf_file, doc, 2000, 100)
        print(f"----\n\n GOT TEXTS {i}")
        # for page in pdf.pages:
        #     page_txt = page.extract_text()
        #     texts.append(page_txt)
        self.pdf_contents = texts
        return self

    def get_first_file_link(self) -> str:
        if self.resources == "None":
            return ""
        f = self.resources[0]["link"]
        return f

    def __init__(self, entry):
        self.link = entry.get("link", "none")
        self.resources = entry.get("resources", "None")
        self.authors = entry.get("authors", "none")
        self.title = entry.get("title", "none")
        self.snippet = entry.get("snippet", "no snippet")

    def toDict(self):
        return {
            "title": self.title,
            "snippet": self.snippet,
            "link": self.snippet,
            "files": self.resources,
            "authors": self.authors,
            "contents": "\n".join(x.text for x in self.pdf_contents) + "...",
        }


import concurrent.futures


# Function to process each item
def process_item(item):
    # return run_timeout(item.set_pdf_contents, timeout=5, content_url=item.get_first_file_link())
    return run_with_timeout(
        item[0].set_pdf_contents, timeout=10, content_url=item[0].get_first_file_link(), i=item[1]
    )

    # return item.set_pdf_contents(content_url=item.get_first_file_link())


# List of data items to process
def process(data_filtered):
    data_filtered = list(zip(data_filtered, range(len(data_filtered))))
    # Use ThreadPoolExecutor to run the tasks in parallel
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Map the process_item function to each item in data_filtered
        result = executor.map(process_item, data_filtered[:-1])
    return result
