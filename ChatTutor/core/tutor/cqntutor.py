## TODO: transform this into NSF center

from .systemmsg import default_system_message
from ..openai_tools import OPENAI_DEFAULT_MODEL
from ..openai_tools import OPENAI_DEFAULT_MODEL
from core.tutor.systemmsg import default_system_message, cqn_system_message
from core.tutor.tutor import Tutor
from abc import ABC, ABCMeta, abstractmethod
from enum import Enum
from nice_functions import pprint, bold, green, blue, red, time_it
from core.tutor.utils import truncate_to_x_number_of_tokens, get_number_of_tokens


class CQNTutor(Tutor):
    def __init__(
        self, embedding_db, embedding_db_name="CQN database", engineer_prompts=True, gemini=True
    ):
        self.gemini = gemini
        super().__init__(embedding_db, embedding_db_name, cqn_system_message, engineer_prompts)

    def get_paper_titles_from_prompt_openai(self, prompt):
        # print("entering get_type_of_question")
        paper_titles_from_prompt = time_it(self.simple_gpt, "required_level_of_information")(
            f"""
           You will get a question, or a summary of a conversation between a bot and a user. 
           Your goal is identify if one or more scientific papers or research articles are mentioned in the conversation, and if yes, then to extract the article titles.
           You will return a list in python style.
           If there are not papers, just respond with "NO".

        """,
            f"""Which paper titles can you identify in this sentence? "{prompt}""",
            temperature=0.5,
        )
        return paper_titles_from_prompt

    def get_required_level_of_information_openai(self, prompt, explain=False):
        respond_with = ""
        if explain:
            respond_with = "Explain why"

        # print("entering get_type_of_question")
        required_level_of_information = time_it(self.simple_gpt, "required_level_of_information")(
            f"""
            There is a database of papers, containing:
                - "paper title"
                - "paper authors"
                - "very short paper summary"
                - "full paper content"
                - "publishing date"
                - "paper url"
            There is also a text summary containing:
                - "the total number of papers in the database"
                - "the total number of papers per research area"
            These 8 elements of the list are what we call "pieces of information"    

            To determine if a paper is present in the database, we can search by "paper title", "paper authors" and "publishing date".
            To make a paper summary, the "full paper content" is required.
            To answer questions about physics concepts, theories, laws, equations, the "full paper content" of the papers is required.
            To know the research area of the paper, the field of study, or if they are related to a topic, then the "very short paper summary" is required.
            To list papers in a research area, a field of study or a branch of physics, then the "very short paper summary" is required.
            To find similar papers, "very short paper summary" would be enought.
            If someone ask to summarize the content of the database, we will provide only "the total number of papers" and "the total number of papers per research area".
            To list papers, "paper title", "paper authors", "publishing date" and "paper url" is required.
            {respond_with}            
        """,
            f"""if the user ask for "{prompt}", which "pieces of information" are required to answer his questions. Just mention what is necessary, nothing else""",
            temperature=0.5,
        )

        if explain:
            pprint(required_level_of_information)
        required_level_of_information = required_level_of_information.lower()
        if "full paper content" in required_level_of_information:
            return "high"
        elif "paper summary" in required_level_of_information:
            return "medium"
        elif "the total number" in required_level_of_information:
            return "db_summary"
        else:
            return "basic"

    def get_paper_titles_from_prompt(self, prompt):
        if self.gemini == False:
            return self.get_paper_titles_from_prompt(prompt)
        # print("entering get_type_of_question")
        paper_titles_from_prompt = time_it(self.genai_model.generate_content, "generate_content")(
            [
                f"""
            You will get a question, or a summary of a conversation between a bot and a user. 
            Your goal is identify if one or more scientific papers or research articles are mentioned in the conversation, and if yes, then to extract the article titles.
            You will return a list in python style.
            If there are not papers, just respond with "NO".

            """,
                f"""Which paper titles can you identify in this sentence? "{prompt}""",
            ]
        )
        paper_titles_from_prompt.resolve()
        return paper_titles_from_prompt.text

    def get_required_level_of_information(self, prompt, explain=False):
        if self.gemini == False:
            return self.get_required_level_of_information_openai(prompt, explain)
        respond_with = ""
        if explain:
            respond_with = "Explain why"

        # print("entering get_type_of_question")
        required_level_of_information = time_it(
            self.genai_model.generate_content, "required_level_of_information"
        )(
            [
                f"""
            There is a database of papers, containing:
                - "paper title"
                - "paper authors"
                - "very short paper summary"
                - "full paper content"
                - "publishing date"
                - "paper url"
            There is also a text summary containing:
                - "the total number of papers in the database"
                - "the total number of papers per research area"
            These 8 elements of the list are what we call "pieces of information"    

            To determine if a paper is present in the database, we can search by "paper title", "paper authors" and "publishing date".
            To make a paper summary, the "full paper content" is required.
            To answer questions about physics concepts, theories, laws, equations, the "full paper content" of the papers is required.
            To know the research area of the paper, the field of study, or if they are related to a topic, then the "very short paper summary" is required.
            To list papers in a research area, a field of study or a branch of physics, then the "very short paper summary" is required.
            To find similar papers, "very short paper summary" would be enought.
            If someone ask to summarize the content of the database, we will provide only "the total number of papers" and "the total number of papers per research area".
            To list papers, "paper title", "paper authors", "publishing date" and "paper url" is required.
            {respond_with}            
        """,
                f"""if the user ask for "{prompt}", which "pieces of information" are required to answer his questions. Just mention what is necessary, nothing else""",
            ]
        )

        # if explain:
        pprint(required_level_of_information)
        required_level_of_information.resolve()
        required_level_of_information = required_level_of_information.text.lower()
        if "full paper content" in required_level_of_information:
            return "high"
        elif "paper summary" in required_level_of_information:
            return "medium"
        elif "the total number" in required_level_of_information:
            return "db_summary"
        else:
            return "basic"

    def get_metadata_from_paper_titles_from_prompt(self, paper_titles_from_prompt):
        paper_titles_from_prompt = paper_titles_from_prompt.replace('"', "")
        paper_titles_from_prompt = paper_titles_from_prompt.replace("[", "")
        paper_titles_from_prompt = paper_titles_from_prompt.replace("]", "")
        self.embedding_db.load_datasource(f"cqn_ttvv_titles")
        (
            documents,
            metadatas,
            distances,
            documents_plain,
        ) = time_it(
            self.embedding_db.query
        )(paper_titles_from_prompt, 10, None, metadatas=True)
        metadata_from_paper_titles_from_prompt = []
        for meta, dist in zip(metadatas, distances):
            if dist < 0.2:
                metadata_from_paper_titles_from_prompt.append(meta)
        return metadata_from_paper_titles_from_prompt

    def process_prompt(
        self, conversation, from_doc=None, threshold=0.5, limit=3, pipeline="openai"
    ):
        id
        # Ensuring the last message in the conversation is a user's question
        assert (
            conversation[-1]["role"] == "user"
        ), "The final message in the conversation must be a question from the user."
        conversation = self.truncate_conversation(conversation)

        prompt = conversation[-1]["content"]
        required_level_of_information = self.get_required_level_of_information(prompt=prompt)
        pprint("required_level_of_information ", green(required_level_of_information))

        # todo: fix prompt to take context from all messages
        (
            prompt,
            is_generic_message,
            is_furthering_message,
            get_furthering_message,
        ) = time_it(self.engineer_prompt)(
            conversation, context=False  # self.engineer_prompts
        )  # if contest is st to False, it is equivalent to conversation[-1]["content"]
        # Querying the database to retrieve relevant documents to the user's question
        arr = []
        # add al docs with distance below threshold to array

        paper_titles_from_prompt = self.get_paper_titles_from_prompt(prompt)
        pprint("paper_titles_from_prompt", paper_titles_from_prompt)

        metadata_from_paper_titles_from_prompt = self.get_metadata_from_paper_titles_from_prompt(
            paper_titles_from_prompt
        )
        pprint(
            "metadata_from_paper_titles_from_prompt",
            metadata_from_paper_titles_from_prompt,
        )

        valid_docs = []
        query_limit = 0
        process_limit = 0
        show_limit = 0

        if (
            "cqn_ttvv" in str(self.collections.items())
            and required_level_of_information == "db_summary"
        ):
            import db_summary

            docs = db_summary.get_db_summary()

        else:
            for coll_name, coll_desc in self.collections.items():
                # if is_generic_message:
                #    continue
                if self.embedding_db:
                    keep_only_first_x_tokens_for_processing = None  # none means all
                    if coll_name == "cqn_ttvv" and required_level_of_information == "basic":
                        self.embedding_db.load_datasource(f"{coll_name}")
                        query_limit = 100
                        process_limit = 20  # each basic entry has close to 100 tokens
                        show_limit = 0
                    elif coll_name == "cqn_ttvv" and required_level_of_information == "medium":
                        self.embedding_db.load_datasource(f"{coll_name}")
                        query_limit = 100
                        process_limit = 10  # each basic entry has close to 350 tokens
                        keep_only_first_x_tokens_for_processing = 200
                        show_limit = 3
                    else:
                        required_level_of_information = "high"
                        self.embedding_db.load_datasource(coll_name)
                        query_limit = 10
                        process_limit = 3  # each is close to 800
                        show_limit = 3

                        if (
                            metadata_from_paper_titles_from_prompt
                            and len(metadata_from_paper_titles_from_prompt) == 1
                        ):
                            pprint(
                                "Adding 'from_doc' filter!",
                                metadata_from_paper_titles_from_prompt[0]["doc"],
                            )
                            from_doc = metadata_from_paper_titles_from_prompt[0]["doc"]
                            process_limit = 3
                            show_limit = 1

                    pprint(
                        "\nQuerying embedding_db with prompt:",
                        blue(prompt),
                        self.embedding_db.datasource,
                    )

                    (
                        documents,
                        metadatas,
                        distances,
                        documents_plain,
                    ) = time_it(
                        self.embedding_db.query
                    )(prompt, query_limit, from_doc, metadatas=True)
                    pprint(rf"got {len(documents)} documents")
                    for doc, meta, dist in zip(documents, metadatas, distances):
                        pprint(green(doc), dist, "\n")
                        # if no fromdoc specified, and distance is lowe thhan thersh, add to array of possible related documents
                        # if from_doc is specified, threshold is redundant as we have only one possible doc
                        if dist <= threshold or from_doc != None or pipeline == "gemini":
                            arr.append(
                                {
                                    "coll_desc": coll_desc,
                                    "coll_name": coll_name,
                                    "doc": doc,
                                    "metadata": meta,
                                    "distance": dist,
                                }
                            )
            sorted_docs = sorted(arr, key=lambda el: el["distance"])
            valid_docs = sorted_docs[:process_limit]

            # print in the console basic info of valid docs
            pprint("valid_docs : ", len(valid_docs))
            for idoc, doc in enumerate(valid_docs):
                pprint(f"- {idoc}", doc["metadata"].get("docname", "(not defined)"))
                pprint(" ", doc["metadata"].get("authors", "(not defined)"))
                pprint(" ", doc["metadata"].get("pdf_url", "(not defined)"))
                pprint(" ", doc["distance"])

            # pprint("system_message", self.system_message)
            # stringify the docs and add to context message
            docs = ""
            if required_level_of_information in {"basic", "medium"}:
                docs = "\n\n"
                docs += "IMPORTANT: if the user asks information about papers, ALWAYS asumme they want information related to the provided list of papers. All these papers belong to the Quantum Networks Database (CQN database). If there is a list, there must (most of the times) be answer!"
                docs += "The following is the list of papers from the Quantum Networks Database (CQN database) that must be used as source of information to answer the user's question:\n\n"
                for doc in valid_docs:
                    doc_content = truncate_to_x_number_of_tokens(
                        doc["doc"], keep_only_first_x_tokens_for_processing
                    )
                    collection_db_response = doc_content
                    docs += collection_db_response + "\n"
                docs += "The 'provided list of papers' finish here."
            else:
                for doc in valid_docs:

                    doc_title_or_file_name = doc["metadata"].get("title", None) or doc[
                        "metadata"
                    ].get("doc", None)
                    doc_authors = ""
                    doc_content = doc["doc"]
                    if doc["metadata"].get("authors"):
                        doc_authors = doc["metadata"].get("authors")
                        doc_authors += rf" by '{doc_authors}'"

                    doc_content = (
                        rf"Paper Title:'{doc_title_or_file_name}'{doc_authors}: {doc_content}"
                    )
                    doc_content = truncate_to_x_number_of_tokens(
                        doc_content, keep_only_first_x_tokens_for_processing
                    )

                    doc_reference = "-" * 100 + f"\n{doc_content}\n\n"
                    docs += doc_reference
                # print('#### COLLECTION DB RESPONSE:', collection_db_response)
            # debug log
        pprint("collections", self.collections)
        pprint("len collections", len(self.collections))

        # Creating a chat completion object with OpenAI API to get the model's response
        messages = [{"role": c["role"], "content": c["content"]} for c in conversation]
        if self.embedding_db and len(self.collections) > 0:
            messages = [
                {"role": "system", "content": self.system_message.format(docs=docs)}
            ] + messages
        pprint("len messages", len(messages))
        pprint("messages", messages)
        total_tokens = get_number_of_tokens(str(messages))
        docs_tokens = get_number_of_tokens(docs)
        pprint("total_tokens", total_tokens)
        pprint("docs_tokens", docs_tokens)

        return messages, valid_docs
