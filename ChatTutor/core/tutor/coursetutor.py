from ..openai_tools import OPENAI_DEFAULT_MODEL
from core.tutor.systemmsg import default_system_message
from core.tutor.tutor import Tutor
from abc import ABC, ABCMeta, abstractmethod
from enum import Enum
from nice_functions import pprint, bold, green, blue, red, time_it


class CourseTutor(Tutor):
    def __init__(
        self,
        embedding_db,
        embedding_db_name: str,
        system_message: str = default_system_message,
        engineer_prompts: bool = True,
    ):
        super().__init__(embedding_db, embedding_db_name, system_message, engineer_prompts)

    @abstractmethod
    def get_collection_valid_docs(
        self, prompt, coll_name, coll_desc, from_doc=None, threshold=0.5, query_limit=3
    ):
        """_summary_

        Args:
            prompt (str): prompt message
            coll_name (str): collection name
            coll_desc (str): collection desc
            from_doc (str | list[str], optional): doc(s) to pull from. Defaults to None.
            threshold (float, optional): Maximum distance from the query. Defaults to 0.5.
            query_limit (int, optional): Maximum documents to be returned. Defaults to 3.

        Advised Return:
            ```
            list[{
                "coll_desc": str, # collection description or empty
                "coll_name": str, # collection name,
                "doc": doc , # document returned
                "metadata": meta, # metadata
                "distance": float, # distance from the query
            }]
            ```
            : the valid documents (closest to the query)
            that will be used as knowledge base by the tutor
        """
        pass

    def get_valid_docs(self, prompt, from_doc=None, threshold=0.5, limit=3):
        """Gets valid docs for each collection in self.collections
        Makes use of the abstract `get_collection_valid_docs` function

        Args:
            prompt (str): prompt message
            from_doc (str | list[str], optional): doc(s) to pull from. Defaults to None.
            threshold (float, optional): Maximum distance from the query. Defaults to 0.5.
            limit (int, optional): Maximum documents to be returned. Defaults to 3.

        Advised Return:
            ```
            list[{
                "coll_desc": str, # collection description or empty
                "coll_name": str, # collection name,
                "doc": doc , # document returned
                "metadata": meta, # metadata
                "distance": float, # distance from the query
            }]
            ```
            : the valid documents (closest to the query)
            that will be used as knowledge base by the tutor
        """
        arr = []
        valid_docs = []
        query_limit = limit * 5
        process_limit = limit + 2  # each is close to 800

        # add all docs with distance below threshold to array
        for coll_name, coll_desc in self.collections.items():
            # if is_generic_message:
            #    continue
            if self.embedding_db and coll_name != None:
                print(f"Collection: {coll_name}")
                self.embedding_db.load_datasource(coll_name)
                arr = arr + self.get_collection_valid_docs(
                    prompt, coll_name, coll_desc, from_doc, threshold, query_limit
                )

        # sort by distance, increasing
        sorted_docs = sorted(arr, key=lambda el: el["distance"])
        valid_docs = sorted_docs[:process_limit]
        pprint(blue("Array begin"))

        pprint(f"Documents: {arr}")
        pprint(blue(f"Array length: {len(valid_docs)}"))
        return valid_docs

    def prettify(self, valid_docs):
        """Generate string of valid documents

        Args:
            valid_docs : documents

        Returns:
            string: string containing the docs' contents
        """
        docs = ""
        for doc in valid_docs:
            doc_title_or_file_name = doc["metadata"].get("title", None) or doc["metadata"].get(
                "doc", None
            )
            doc_authors = ""
            doc_content = doc["doc"]
            if doc["metadata"].get("authors"):
                doc_authors = doc["metadata"].get("authors")
                doc_authors += rf" by '{doc_authors}'"

            doc_content = (
                rf"Course section at:'{doc_title_or_file_name}', by {doc_authors}: {doc_content}"
            )
            doc_reference = "-" * 100 + f"\n{doc_content}\n\n"
            docs += doc_reference
        return docs

    def debug_log_valid_docs(self, valid_docs):
        """Log valid_docs

        Args:
            valid_docs (doc): documents
        """
        pprint("valid_docs")
        for idoc, doc in enumerate(valid_docs):
            pprint(
                f"- {idoc}",
                doc["metadata"].get("docname", "(not defined)"),
                "/",
                doc["metadata"].get("doc", "(not defined)"),
            )
            pprint(" ", doc["metadata"].get("authors", "(not defined)"))
            pprint(" ", doc["metadata"].get("pdf_url", "(not defined)"))
            pprint(" ", doc["distance"])

        pprint("collections", self.collections)
        pprint("len collections", len(self.collections))

    def process_prompt(
        self, conversation, from_doc=None, threshold=0.5, limit=3, pipeline="openai"
    ):
        print("\n\n")
        print("#" * 100)
        print("beggining ask_question:")

        if pipeline != "openai":
            self.engineer_prompts = False
        # Ensuring the last message in the conversation is a user's question
        assert (
            conversation[-1]["role"] == "user"
        ), "The final message in the conversation must be a question from the user."
        conversation = self.truncate_conversation(conversation)

        prompt = conversation[-1]["content"]

        (
            prompt,
            is_generic_message,
            is_furthering_message,
            get_furthering_message,
        ) = time_it(self.engineer_prompt)(
            conversation, context=self.engineer_prompts
        )  # if contest is st to False, it is equivalent to conversation[-1]["content"]
        # Querying the database to retrieve relevant documents to the user's question
        pprint(blue(prompt))
        valid_docs = self.get_valid_docs(prompt, from_doc, threshold, limit)
        self.debug_log_valid_docs(valid_docs)
        docs = self.prettify(valid_docs)

        messages = [{"role": c["role"], "content": c["content"]} for c in conversation]
        if self.embedding_db and len(self.collections) > 0:
            messages = [
                {"role": "system", "content": self.system_message.format(docs=docs)}
            ] + messages
        pprint("len messages: ", len(messages))
        pprint("messages: ", messages)
        return messages, valid_docs
