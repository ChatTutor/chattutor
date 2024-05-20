import uuid
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

from core.data.models.Citations import Citations
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
from core.data.models.Author import Author
from core.data.models.Publication import Publication
from google_scholar_py import *
from core.reader import parse_pdf, Text, Doc
import multiprocessing
from serpapi import GoogleScholarSearch

from core.vectordatabase import VectorDatabase


def run_with_timeout(func, timeout, *args, **kwargs):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(func, *args, **kwargs)
        try:
            result = future.result(timeout=timeout)
            return result
        except concurrent.futures.TimeoutError:
            print("[TIMEOUT] on function")
            return None


def load_citations(data):
    dt = GoogleScholarSearch(
        {
            "api_key": os.getenv("SERP_API_KEY"),
            "engine": "google_scholar_cite",
            "q": data.entry["result_id"],
        }
    )
    print(f"\n\n{dt.get_json()}\n\n")
    data.citations_unpacked = dt.get_dictionary()
    return data


class CQNPublications:
    title: str
    snippet: str
    link: str
    resources: List
    authors: List
    pdf_contents: List[Text] = []
    citations_unpacked: dict = {}
    result_id: str

    def set_pdf_contents(self, content_url, i):
        doc = Doc(docname=f"{self.result_id}", citation=f"{content_url}", dockey=f"{self.result_id}")

        texts = []
        content_url = content_url.replace("html", "pdf")
        resp = requests.get(content_url)
        print(f"\n\n{content_url}:\n")
        open_pdf_file = resp.content
        print(f"\n\tGettng texts {i}\n")
        texts = parse_pdf(open_pdf_file, doc, 2000, 100)
        x = load_citations(self)
        self.citations_unpacked = x.citations_unpacked
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
        print(entry)
        self.link = entry.get("link", "None")
        self.resources = entry.get("resources", "None")
        self.publication_info = entry.get("publication_info", "{}")
        self.authors = self.publication_info.get("authors", "None")
        self.title = entry.get("title", "None")
        self.snippet = entry.get("snippet", "None")
        self.entry = entry
        self.result_id = entry.get("result_id", "None")

    def toDict(self):
        return {
            "title": self.title,
            "snippet": self.snippet,
            "link": self.snippet,
            "files": self.resources,
            "authors": self.authors,
            "entry": self.entry,
            "contents": "\n".join(x.text for x in self.pdf_contents) + "...",
            "citations_unpacked": self.citations_unpacked,
        }


import concurrent.futures


# Function to process each item
def process_item(item):
    # return run_timeout(item.set_pdf_contents, timeout=5, content_url=item.get_first_file_link())
    return run_with_timeout(
        item[0].set_pdf_contents, timeout=20, content_url=item[0].get_first_file_link(), i=item[1]
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


class PaperManager:
    @staticmethod
    def add_to_database(dt: List[CQNPublications]):
        authors: List[Author] = []
        citations: List[Citations] = []
        print(f" --- ADDING {len(dt)} BOOKS to ANDU --- ", )
        for book in dt:
            print(f"BOOK::{book.result_id}:{book.title}:{book.link}")
            for author in book.authors:
                author_model = Author(author_id=author.get('author_id', 'none'), link=author.get('link', 'none'),
                                      name=author.get('name', 'none'),
                                      serpapi_scholar_link=author.get('serpapi_scholar_link', 'none'),
                                      cqn_pub_id=author.get('author_id', 'none'))
                authors.append(author_model)

            for citation in book.citations_unpacked.get('citations', []):
                citation_id = f'{uuid.uuid4()}';
                citation_model = Citations(citation_id=citation_id, snippet=citation.get('snippet', 'none'),
                                           title=citation.get('title', 'none'), cqn_pub_id=citation_id)
                citations.append(citation_model)

            model = Publication(result_id=book.result_id, link=book.link,
                                snippet=book.snippet, title=book.title, chroma_doc_id=book.result_id)
            DataBase().insert_paper(model=model, citations=citations, authors=authors)

    @staticmethod
    def add_to_chroma(dt: List[CQNPublications]):
        authors: List[Author] = []
        citations: List[Citations] = []


        print(f" --- ADDING {len(dt)} BOOKS --- ", )
        for book in dt:
            doc = Doc(docname=f"{book.result_id}", citation=f"{book.link}", dockey=f"{book.result_id}")
            authors_text_all: Text = Text(text=f'Paper {book.title}, id: {book.result_id} written by authors:\n', doc=doc)
            citations_text_all: Text = Text(text=f'Paper {book.title}, id: {book.result_id} has the following papers cited:\n', doc=doc)
            titles_text_all: Text = Text(text=f'Paper {book.result_id} has the title: {book.title}\n', doc=doc)
            titles_text_reverse_all: Text = Text(text=f'{book.title} is the title of {book.result_id}\n', doc=doc)
            titles_text_reverse_just: Text = Text(text=f'{book.title}\n', doc=doc)
            for author in book.authors:

                author_model = Author(author_id=author.get('author_id', 'none'), link=author.get('link', 'none'),
                                      name=author.get('name', 'none'),
                                      serpapi_scholar_link=author.get('serpapi_scholar_link', 'none'),
                                      cqn_pub_id=author.get('author_id', 'none'))
                authors_text_all.text += (f'Name: {author_model.name}\nId: {author_model.author_id}\nLink: '
                                          f'Author link: {author_model.link}\nSerp_api_scholar_link: '
                                          f'{author_model.serpapi_scholar_link}\n\n')

                authors.append(author_model)

            for citation in book.citations_unpacked.get('citations', []):
                citation_id = f'{uuid.uuid4()}'
                citation_model = Citations(citation_id=citation_id, snippet=citation.get('snippet', 'none'),
                                           title=citation.get('title', 'none'), cqn_pub_id=citation_id)

                citations_text_all.text += (f'Id: {citation_model.citation_id}\nSnippet: {citation_model.snippet}\n'
                                            f'Title: {citation_model.title}\n\n')
                citations.append(citation_model)


            db.load_datasource_papers('cqn_may')

            content_texts: List[Text] = book.pdf_contents

            db.add_texts_papers(content_texts)
            db.add_texts_papers([authors_text_all], "authors")
            db.add_texts_papers([titles_text_all, titles_text_reverse_all, titles_text_reverse_just], "titles")
            db.add_texts_papers([citations_text_all], "citations")
