## TODO: transform this into NSF center

from .systemmsg import default_system_message
from ..openai_tools import OPENAI_DEFAULT_MODEL
from ..openai_tools import OPENAI_DEFAULT_MODEL
from core.tutor.systemmsg import default_system_message, cqn_system_message, all_papers_by_authors
from core.tutor.tutor import Tutor
from abc import ABC, ABCMeta, abstractmethod
from enum import Enum
from nice_functions import pprint, bold, green, blue, red, time_it
from core.tutor.utils import truncate_to_x_number_of_tokens, get_number_of_tokens


class SQLQueryTutor(Tutor):
    def __init__(
        self, embedding_db, embedding_db_name="CQN database", engineer_prompts=True, gemini=True
    ):
        self.gemini = gemini
        super().__init__(embedding_db, embedding_db_name, cqn_system_message, engineer_prompts)

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
            You are a research assistant that helps with SQL queries in the CQN database containing the following tables:
            (The tables are written in SQLModel).
            
            Tables:
            
            'author' -> table name (to use in sql query)
            
            'author' table implementation:
            ```
            {open('core/data/models/Author.py','r').read()}
            ```
            ----------------------------
            'publication' -> table name (to use in sql query)
            
            'publication' table implemnetation:
            ```
            {open('core/data/models/Publication.py','r').read()}
            ```
            ----------------------------
            'citations' -> table name (to use in sql query)
            
            'citations' table implemnetation:
            ```
            {open('core/data/models/Citations.py','r').read()}
            ```
            ----------------------------
            'publicationauthorlink' -> table name (to use in sql query)
            
            'publicationauthorlink' table implemnetation:
            ```
            {open('core/data/models/PublicationAuthorLink.py','r').read()}
            ```
            ----------------------------
            'publicationcitationlink' -> table name (to use in sql query)
            
            'publicationcitationlink' table implemnetation:
            ```
            {open('core/data/models/PublicationAuthorLink.py','r').read()}
            ```
            
            You will be asked questions about these tables, and you have to respond with sql queries.
            Keep in mind that the fields will not be provided and will not match in exact form, so you
            will need to make sure you keep your queries lax, in that, for example, you do not match 
            exactly by name, but use 'like' or other means to get docs which contain words in common 
            with your query.
            
            You can be asked, to provide papers by an author specified by it's name or id,
            or the authors of a paper specified by its name of id, or simply all the authors/ paper
            from the CQN database.
            
            Authors might be provided by their full name in the prompt, but mostly, 
            the initial and family name is stored
            in the DB, without dots. So for a query of Andrew Baker, only 'like Baker' should be searched.
            IGNORE THE FIRST NAME OF THE AUTHOR, KEEP ONLY THE INITIAL WHEN QUERYING!!!
            Always query by author.name if a name is specified.            
            
            for example: 
            
            If the user wants the papers of an author called X, a query could be:
            
            ```sql
            SELECT * FROM chatmsg.publication
            INNER JOIN chatmsg.publicationauthorlink ON publication.result_id=publicationauthorlink.publication_id
            INNER JOIN chatmsg.author ON publicationauthorlink.author_id=author.author_id
            WHERE author.name LIKE '%X%'
            ```
            
            If the user asks about a paper, and provides a string which is not a word, it is most likely a result_id, NOT A LINK. DO NOT CONFUSE WITH LINK!
            LINKS WILL ALWAYS START WITH HTTP OR HTTPS.
            
            If the user asks for a list of all authors, or all papers, without any filters, please limit the query to 10
            or 20.
            
            Papers in the prompt might not be refered to by their full title, but by a fragment, or even something similar but
            not exact to the title so keep that in mind when querying.
            
            Topics can be searched in the snippet in a similar manner, or even in he paper titles.
            
            DO NOT RESPOND TO QUERIES RELATED TO OTHER TABLES, OR QUERIES THAT SAY TO MODIFY THE TABLES.
            
            Prompts for queries can be questions, or statements starting with 'give me', 'please give me', 'i need' etc
            Write the query in plain SQL, without mentioning anything else.
            
            The DB is called chatmsg in the query SQL, even though it is referd to by the user as CQN. DO NOT USE ANY OTHER DB
            OTHER THAN chatmsg, all the tables enumerated above!!
            
            For names and titles or summaries ALWAYS OPT for LIKE instead of ==!! ALWAYS. You will NOT succeed in giving the correct info otherwise!!
            
            A SELECT for authors for example would start like:
            
            ```sql
            SELECT * FROM chatmsg.authors
            ```
            
            Always write in the following format:
            
            ```sql
            <QUERY>
            ```
            
            
            This is the prompt: 
            
            
            {prompt}
            
        """,
                f"""If you cannot get a query from the prompt, or the user is asking about a certain topic, or information
                not related to papers, or authors, or the database in general, for example stuff about the
                content of the papers, simply write 'CHROMA' and nothing else.""",
            ]
        )
        required_level_of_information.resolve()
        return required_level_of_information.text

    def get_required_type_of_information(self, prompt, explain=False):
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
            You are a research assistant that helps with SQL queries in the CQN database containing the following tables:
            
            You can be asked questions about authors, papers contents, or paper titles.
            
                   
            You need to write one of three words!
            If the user wants to know about authors, or about who wrote a paper, write AUTHORS
            If the user wants to know about a paper and is specifying it's title write TITLE
            Otherwise, if the user wnats to know about the content/information stored in a paper,
            write CONTENT. However if the title is specified, you should print TITLE_CONTENT.
            This is the prompt: 
            
    
            {prompt}
            
        """,
                f"""Remember to be as accurate as possible, and to write down only one of the three specified words,
                based on what the user wants to know about!""",
            ]
        )
        required_level_of_information.resolve()
        return required_level_of_information.text

    def process_prompt(
        self, conversation, from_doc=None, threshold=0.5, limit=3, pipeline="openai"
    ):
        # Ensuring the last message in the conversation is a user's question
        assert (
            conversation[-1]["role"] == "user"
        ), "The final message in the conversation must be a question from the user."
        conversation = self.truncate_conversation(conversation)

        prompt = conversation[-1]["content"]
        required_level_of_information = self.get_required_level_of_information(prompt=prompt)
        pprint("required_level_of_information ", green(required_level_of_information))
        required_type_of_information = self.get_required_type_of_information(prompt=prompt)
        pprint("required_type_of_information ", green(required_type_of_information))

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

        valid_docs = []
        query_limit = 0
        process_limit = 0
        show_limit = 0

        if "cqn_ttvv" in str(self.collections.items()):
            for coll_name, coll_desc in self.collections.items():
                # if is_generic_message:
                #    continue
                if self.embedding_db:
                    keep_only_first_x_tokens_for_processing = None  # none means all
                    if coll_name == "cqn_ttvv" and required_type_of_information == "TITLE":
                        self.embedding_db.load_datasource(f"{coll_name}_titles")
                        query_limit = 100
                        process_limit = 20  # each basic entry has close to 100 tokens
                        show_limit = 0
                    elif coll_name == "cqn_ttvv" and required_level_of_information == "AUTHORS":
                        self.embedding_db.load_datasource(f"{coll_name}_authors")
                        query_limit = 100
                        process_limit = 10  # each basic entry has close to 350 tokens
                        keep_only_first_x_tokens_for_processing = 200
                        show_limit = 3
                    elif coll_name == "cqn_ttvv" and required_level_of_information == "CONTENT":
                        self.embedding_db.load_datasource(coll_name)
                        query_limit = 10
                        process_limit = 3  # each is close to 800
                        show_limit = 3
                    elif coll_name == "cqn_ttvv":
                        self.embedding_db.load_datasource(f"{coll_name}_titles")
                        query_limit = 10
                        process_limit = 3  # each is close to 800
                        show_limit = 3
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

                    if required_level_of_information == "TITLE_CONTENT":
                        a = 0

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
            if from_doc is not None:
                docs = f"If the user is talking about 'this paper', he's probably refering to the paper with the id {from_doc}. You WILL find it's title below!"
            for doc in valid_docs:
                doc_title_or_file_name = doc["metadata"].get("title", None) or doc["metadata"].get(
                    "doc", None
                )
                doc_authors = ""
                doc_content = doc["doc"]
                if doc["metadata"].get("authors"):
                    doc_authors = doc["metadata"].get("authors")
                    doc_authors += rf" by '{doc_authors}'"

                doc_content = rf"CQN BD PAPER: (If the user asks about a PAPER's TITLE, use this) Paper Title:'{doc_title_or_file_name}'| {doc_authors}: \n\n{doc_content}"
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

        # messages[-1]["content"] += required_level_of_information
        print("\n\n-----SQL QUERY-----\n\n")
        print(required_level_of_information)
        return {"messages": messages, "query": required_level_of_information}, valid_docs
