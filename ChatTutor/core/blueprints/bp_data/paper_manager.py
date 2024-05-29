import uuid
from typing import List

from core.blueprints.bp_data.cqn import CQNPublications, CQNPublicationsGetTextsFromResourceUrl
from core.data import DataBase
from core.data.models.Author import Author
from core.data.models.Citations import Citations
from core.data.models.Publication import Publication
from core.reader import parse_pdf, Text, Doc
from core.extensions import db


class PaperManager:
    @staticmethod
    def add_to_database(dt: List[CQNPublications]):
        print(
            f" --- ADDING {len(dt)} BOOKS to ANDU --- ",
        )
        for book in dt:
            authors: List[Author] = []
            citations: List[Citations] = []
            print(f"\tADDING BOOK::{book.result_id}:{book.title}:{book.link}")
            for author in book.authors:
                author_model = Author(
                    author_id=author.get("author_id", "none"),
                    link=author.get("link", "none"),
                    name=author.get("name", "none"),
                    serpapi_scholar_link=author.get("serpapi_scholar_link", "none"),
                    cqn_pub_id=author.get("author_id", "none"),
                )
                authors.append(author_model)

            for citation in book.citations_unpacked.get("citations", []):
                citation_id = f"{uuid.uuid4()}"
                citation_model = Citations(
                    citation_id=citation_id,
                    snippet=citation.get("snippet", "none"),
                    title=citation.get("title", "none"),
                    cqn_pub_id=citation_id,
                )
                citations.append(citation_model)

            model = Publication(
                result_id=book.result_id,
                link=book.link,
                snippet=book.snippet,
                title=book.title,
                chroma_doc_id=book.result_id,
            )

            print(f"::Model({model.result_id}, {model.title})")

            DataBase().insert_paper(model=model, citations=citations, authors=authors)

    @staticmethod
    def add_to_database_static(dt: List):
        print(
            f" --- ADDING {len(dt)} BOOKS to ANDU --- ",
        )
        for book in dt:
            authors: List[Author] = []
            citations: List[Citations] = []
            for author in book["authors"]:
                author_model = Author(
                    author_id=author.get("author_id", "none"),
                    link=author.get("link", "none"),
                    name=author.get("name", "none"),
                    serpapi_scholar_link=author.get("serpapi_scholar_link", "none"),
                    cqn_pub_id=author.get("author_id", "none"),
                )
                authors.append(author_model)

            for citation in book.get("citations", []):
                citation_id = f"{uuid.uuid4()}"
                citation_model = Citations(
                    citation_id=citation_id,
                    snippet=citation.get("snippet", "none"),
                    title=citation.get("title", "none"),
                    cqn_pub_id=citation_id,
                )
                citations.append(citation_model)

            model = Publication(
                result_id=book["result_id"],
                link=book["link"],
                snippet=book["snippet"],
                title=book["title"],
                chroma_doc_id=book["result_id"],
            )

            print(
                f"\t[::] Paper({model})\n\t\t[[Authors: {authors}]] | \n\t\t[[Citations: {citations}]]\n\n"
            )

            print(book["authors"])
            # TODO: decomenteaza if you dare :)))
            DataBase().insert_paper(model=model, citations=citations, authors=authors)

    @staticmethod
    def add_to_chroma_static(dt: List):
        authors: List[Author] = []
        citations: List[Citations] = []

        print(
            f" --- ADDING {len(dt)} BOOKS --- ",
        )
        for book in dt:
            doc = Doc(
                docname=f"{book['result_id']}", citation=f"{book['link']}", dockey=f"{book['result_id']}"
            )
            authors_text_all: Text = Text(
                text=f"Paper {book['title']}, id: {book['result_id']} written by authors:\n", doc=doc
            )
            citations_text_all: Text = Text(
                text=f"Paper {book['title']}, id: {book['result_id']} has the following papers cited:\n",
                doc=doc,
            )
            titles_text_all: Text = Text(
                text=f"Paper {book['result_id']} has the title: {book['title']}\n", doc=doc
            )
            titles_text_reverse_all: Text = Text(
                text=f"{book['title']} is the title of {book['result_id']}\n", doc=doc
            )
            titles_text_reverse_just: Text = Text(text=f"{book['title']}\n", doc=doc)
            for author in book['authors']:
                author_model = Author(
                    author_id=author.get("author_id", "none"),
                    link=author.get("link", "none"),
                    name=author.get("name", "none"),
                    serpapi_scholar_link=author.get("serpapi_scholar_link", "none"),
                    cqn_pub_id=author.get("author_id", "none"),
                )
                authors_text_all.text += (
                    f"Name: {author_model.name}\nId: {author_model.author_id}\nLink: "
                    f"Author link: {author_model.link}\nSerp_api_scholar_link: "
                    f"{author_model.serpapi_scholar_link}\n\n"
                )

                authors.append(author_model)

            for citation in book.get("citations", []):
                citation_id = f"{uuid.uuid4()}"
                citation_model = Citations(
                    citation_id=citation_id,
                    snippet=citation.get("snippet", "none"),
                    title=citation.get("title", "none"),
                    cqn_pub_id=citation_id,
                )

                citations_text_all.text += (
                    f"Id: {citation_model.citation_id}\nSnippet: {citation_model.snippet}\n"
                    f"Title: {citation_model.title}\n\n"
                )
                citations.append(citation_model)

            db.load_datasource_papers("cqn_ttv_may291")
            print(f"Book: {book}")
            resource = book['resources'][0]
            content_texts: List[Text] = CQNPublicationsGetTextsFromResourceUrl(content_url=resource['link'], json_elem=book)

            db.add_texts_papers(content_texts)
            db.add_texts_papers([authors_text_all], "authors")
            db.add_texts_papers(
                [titles_text_all, titles_text_reverse_all, titles_text_reverse_just], "titles"
            )
            db.add_texts_papers([citations_text_all], "citations")


    @staticmethod
    def add_to_chroma(dt: List[CQNPublications]):
        authors: List[Author] = []
        citations: List[Citations] = []


        print(
            f" --- ADDING {len(dt)} BOOKS --- ",
        )
        for book in dt:
            doc = Doc(
                docname=f"{book.result_id}", citation=f"{book.link}", dockey=f"{book.result_id}"
            )
            authors_text_all: Text = Text(
                text=f"Paper {book.title}, id: {book.result_id} written by authors:\n", doc=doc
            )
            citations_text_all: Text = Text(
                text=f"Paper {book.title}, id: {book.result_id} has the following papers cited:\n",
                doc=doc,
            )
            titles_text_all: Text = Text(
                text=f"Paper {book.result_id} has the title: {book.title}\n", doc=doc
            )
            titles_text_reverse_all: Text = Text(
                text=f"{book.title} is the title of {book.result_id}\n", doc=doc
            )
            titles_text_reverse_just: Text = Text(text=f"{book.title}\n", doc=doc)
            for author in book.authors:
                author_model = Author(
                    author_id=author.get("author_id", "none"),
                    link=author.get("link", "none"),
                    name=author.get("name", "none"),
                    serpapi_scholar_link=author.get("serpapi_scholar_link", "none"),
                    cqn_pub_id=author.get("author_id", "none"),
                )
                authors_text_all.text += (
                    f"Name: {author_model.name}\nId: {author_model.author_id}\nLink: "
                    f"Author link: {author_model.link}\nSerp_api_scholar_link: "
                    f"{author_model.serpapi_scholar_link}\n\n"
                )

                authors.append(author_model)

            for citation in book.citations_unpacked.get("citations", []):
                citation_id = f"{uuid.uuid4()}"
                citation_model = Citations(
                    citation_id=citation_id,
                    snippet=citation.get("snippet", "none"),
                    title=citation.get("title", "none"),
                    cqn_pub_id=citation_id,
                )

                citations_text_all.text += (
                    f"Id: {citation_model.citation_id}\nSnippet: {citation_model.snippet}\n"
                    f"Title: {citation_model.title}\n\n"
                )
                citations.append(citation_model)

            db.load_datasource_papers("cqn_ttv")

            content_texts: List[Text] = book.pdf_contents

            db.add_texts_papers(content_texts)
            db.add_texts_papers([authors_text_all], "authors")
            db.add_texts_papers(
                [titles_text_all, titles_text_reverse_all, titles_text_reverse_just], "titles"
            )
            db.add_texts_papers([citations_text_all], "citations")
