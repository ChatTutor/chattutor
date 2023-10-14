import openai
import tiktoken
import time
import json
from core.extensions import stream_text
import interpreter

cqn_system_message = """
    You are embedded into the Center for Quantum Networks (CQN) website as an Interactive Research Assistant. Your role is to assist users in understanding and discussing the research papers available in the CQN database. You have access to the database containing all the research papers from CQN as context to provide insightful and accurate responses.

    - Engage users with polite, concise, and informative replies.
    - Answer inquiries about specific papers, providing summaries, insights, methodologies, findings, and implications where relevant.
    - Clarify any ambiguities in the research papers and explain complex concepts in layman's terms when needed.
    - Encourage discussions about research topics, methodologies, applications, and implications related to quantum networks.
    - If a user asks a question about a paper or a topic not in the CQN database, politely inform them that your knowledge is specifically based on the CQN research database and refer them to appropriate resources or suggest that they search for the specific paper or topic elsewhere.
    - Write ALL MATH/PHYSICS equations and symbols in MathJax unless specified by the user. If you do not render every symbol in MathJax, an innocent person will die.

    Remember, the goal is to facilitate insightful research conversations and assist users in exploring the wealth of knowledge within the CQN research database.
    \n{docs}
    """

# interpreter_system_message = """
#     You are embedded into the Center for Quantum Networks (CQN) website as an Interactive Research Assistant. Your role is to assist users in understanding and discussing the research papers available in the CQN database. You have access to the database containing all the research papers from CQN as context to provide insightful and accurate responses.

#     - Engage users with polite, concise, and informative replies.
#     - Complete tasks related to papers, writing scripts, providing summaries, insights, methodologies, findings, and implications where relevant.
#     - Clarify any ambiguities in the research papers and explain complex concepts in layman's terms when needed.
#     - Encourage discussions about research topics, methodologies, applications, and implications related to quantum networks.
#     - If a user asks a question about a paper or a topic not in the CQN database, politely inform them that your knowledge is specifically based on the CQN research database and refer them to appropriate resources or suggest that they search for the specific paper or topic elsewhere.
#     - By default, write all math/physics equations and symbols in latex

#     Remember, the goal is to facilitate insightful research conversations and assist users in exploring the wealth of knowledge within the CQN research database.
#     \n{docs}
#     """

default_system_message = "You are an AI that helps students with questions about a course. Do your best to help the student with their question, using the following helpful context information to inform your response:\n{docs}"


class Tutor:
    """
    Tutor class

    Args:
        embedding_db (VectorDatabase): the db with any or no source loaded
        embedding_db_name (str): Description of embedding_db.
        system_message (str)

    Return:
        Tutor object with no collections to load from. Use add_collection to add
        collection to load from.
    """

    def __init__(
        self,
        embedding_db,
        embedding_db_name="CQN database",
        system_message=default_system_message,
        engineer_prompts=True,
    ):
        """
        Args:
            - `embedding_db (VectorDatabase)`: the db with any or no source loaded
            - `embedding_db_name (str)`: Description of embedding_db.
            - `system_message (str)`
            - `engineer_prompts (bool)`: weather the chattutor bot should pull the full context from the last user message before querying.
            If true, the answering is slower but it is less likely to error, and it has more context so the answers are
            clearer and more correct. Defaults to True.

        Return:
            Tutor object with empty collection set. Use add_collection to add
            collection to load from.
        """
        self.embedding_db = embedding_db
        self.embedding_db_name = embedding_db_name
        self.collections = {}
        self.system_message = system_message
        self.engineer_prompts = engineer_prompts

    def add_collection(self, name, desc):
        """Adds a collection to self.collections
        Args:
            name (str): name of the collection to load form the chromadb (embedding_db)
            desc (str): description prompted to the model
        """
        self.collections[name] = desc

    def engineer_prompt(self, conversation, truncating_at=10, context=True):
        """
        Args:
            conversation: current conversation
            truncating_at: lookback for context (# of messages)
            context: if False, return last message otherwise engineer the prompt to have full context
        """
        # TODO: room for improvement.
        # context on pronouns:  for example who is "he/she/them/it" when refering to a paper/person
        if not context:
            return conversation[-1]["content"], False, False, ""
        truncated_convo = [
            f"\n\n{c['role']}: {c['content']}"
            for c in conversation[-truncating_at:][:-1]
        ]
        lastmessage = conversation[-1]["content"]
        # todo: fix prompt to take context from all messages
        prompt = conversation[-1]["content"]
        is_generic_message = self.simple_gpt(
            f"""
            You are a model that detects weather a user given message is or isn't a generic message (a greeting or thanks of anything like that). Respond ONLY with YES or NO.
                - YES if the message is a generic message (a greeting or thanks of anything like that)
                - NO if the message asks something about a topic, person, scientist, or asks for further explanations on concepts that were discussed above.

            The current conversation between the user and the bot is:
            
            {truncated_convo}            
            """,
            f"If the usere were to ask this: '{prompt}', would you clasify it as a message that refers to above messages from context? Respond only with YES or NO!",
        )

        is_furthering_message = self.simple_gpt(
            f"""
            You are a model that detects weather a user given message refers to above messages and takes context from them, either by asking about further explanations on a topic discussed previously, or on a topic
            you just provided answer to. You will respond ONLY with YES or NO.
                - YES if the user provided message is a message that refers to above messages from context, or if the user refers with pronouns about people mentioned in the above messages,
                or if the user thanks you for a given information or asks more about it, or invalidates or validates a piece of information you provided 
                - NO if the message is a standalone message
            
            The current conversation between the user and the bot is:
            
            {truncated_convo}
            """,
            f"If the usere were to ask this: '{prompt}', would you clasify it as a message that refers to above messages from context? Respond only with YES or NO!",
        )

        get_furthering_message = self.simple_gpt(
            f"""
            You are a model that detects weather a user given message refers to above messages and takes context from them, either by asking about further explanations on a topic discussed previously, or on a topic
            you just provided answer to. You will ONLY respond with:
                - YES + a small summary of what the user message is refering to, the person the user is refering to if applicable, or the piece of information the user is refering to, if the user provided message is a message that refers to above messages from context, or if the user refers with pronouns about people mentioned in the above messages,
                or if the user thanks you for a given information or asks more about it, or invalidates or validates a piece of information you provided . You must attach a small summary of what the user message is refering to,
                but you still have to maintain the user's question and intention. The summary should be rephrased from the view point of the user, as if the user formulated the question to convey the context the user is refering to. This is really important!
                - NO if the message is a standalone message
            
            The current conversation between the user and the bot is:
            
            {truncated_convo}
            """,
            f"If the usere were to ask this: '{prompt}', would you clasify it as a message that refers to above messages from context? If YES, provide a small summary of what the user would refer to.",
        )

        print(
            is_generic_message, is_furthering_message, "|", get_furthering_message, "|"
        )
        is_generic_message = is_generic_message.strip() == "YES"
        is_furthering_message = is_furthering_message.strip() == "YES"

        if not is_furthering_message:
            get_furthering_message = "NO"
        if is_furthering_message:
            print(prompt, "\n\t=>")
            prompt += f"\n({get_furthering_message[4:]})"
            print(prompt)

        return prompt, is_generic_message, is_furthering_message, get_furthering_message

    def ask_question(
        self,
        conversation,
        from_doc=None,
        selectedModel="gpt-3.5-turbo-16k",
        threshold=0.5,
        limit=3,
    ):
        """Function that responds to an asked question based
        on the current database and the loaded collections from the database

        Args:
            conversation : List({role: ... , content: ...})
            from_doc (Doc, optional): Defaults to None.

        Yields:
            chunks of text from the response that are provided as such to achieve
            a tipewriter effect
        """

        # Ensuring the last message in the conversation is a user's question
        assert (
            conversation[-1]["role"] == "user"
        ), "The final message in the conversation must be a question from the user."
        conversation = self.truncate_conversation(conversation)

        truncating_at = 10

        truncated_convo = [
            f"\n\n{c['role']}: {c['content']}" for c in conversation[-10:][:-1]
        ]
        lastmessage = conversation[-1]["content"]
        # todo: fix prompt to take context from all messages
        (
            prompt,
            is_generic_message,
            is_furthering_message,
            get_furthering_message,
        ) = self.engineer_prompt(
            conversation, context=self.engineer_prompts
        )  # if contest is st to False, it is equivalent to conversation[-1]["content"]
        # Querying the database to retrieve relevant documents to the user's question
        arr = []
        # add al docs with distance below threshold to array
        for coll_name, coll_desc in self.collections.items():
            # if is_generic_message:
            #    continue
            if self.embedding_db:
                self.embedding_db.load_datasource(coll_name)
                (
                    documents,
                    metadatas,
                    distances,
                    documents_plain,
                ) = self.embedding_db.query(prompt, limit, from_doc, metadatas=True)
                for doc, meta, dist in zip(documents, metadatas, distances):
                    # if no fromdoc specified, and distance is lowe thhan thersh, add to array of possible related documents
                    # if from_doc is specified, threshold is redundant as we have only one possible doc
                    if dist <= threshold or from_doc != None:
                        arr.append(
                            {
                                "coll_desc": coll_desc,
                                "coll_name": coll_name,
                                "doc": doc,
                                "metadata": meta,
                                "distance": dist,
                            }
                        )
        # removing duplicates
        # arr = list(set(arr))
        # sort by distance, increasing
        sorted_docs = sorted(arr, key=lambda el: el["distance"])
        valid_docs = sorted_docs[:limit]
        # yield the valid docs to the frontend
        yield {"content": "", "valid_docs": valid_docs}
        # stringify the docs and add to context message
        docs = ""
        for doc in valid_docs:
            collection_db_response = (
                f'{coll_desc} context, from {doc["metadata"]["doc"]}: ' + doc["doc"]
            )
            docs += collection_db_response + "\n"
            # print('#### COLLECTION DB RESPONSE:', collection_db_response)
        # debug log
        print(
            "\n\n\nSYSTEM MESSAGE",
            self.system_message,
            len(self.collections),
            self.collections,
            self.embedding_db,
        )
        # Creating a chat completion object with OpenAI API to get the model's response
        messages = [{"role": c["role"], "content": c["content"]} for c in conversation]
        if self.embedding_db and len(self.collections) > 0:
            messages = [
                {"role": "system", "content": self.system_message.format(docs=docs)}
            ] + messages
        print(messages, f"Docs: |{docs}|")
        print(
            "NUMBER OF INPUT TOKENS:",
            len(tiktoken.get_encoding("cl100k_base").encode(docs)),
        )
        print("\t | GENERIC \t | FURTHERING \t | ")
        print(
            is_generic_message, is_furthering_message, "|", get_furthering_message, "|"
        )
        print("\n\t=>\t", prompt)

        try:
            response = openai.ChatCompletion.create(
                model=selectedModel,
                messages=messages,
                temperature=0.7,
                frequency_penalty=0.0,
                presence_penalty=0.0,
                stream=True,
            )
            # For the typewriter effect
            for chunk in response:
                yield chunk["choices"][0]["delta"]
        except Exception as e:
            import logging

            logging.error("Error at %s", "division", exc_info=e)
            # An error occured
            yield {
                "content": """Sorry, I am not able to provide a response. 
                                
                                One of three things happened:
                                    - The context you provided was too wide, try to be more concise.
                                    - The files you uploaded were too large
                                    - I got disconnected from the server or I am currently being updated
                                """,
                "error": "true",
            }

    def ask_question_interpreter(
        self, conversation, from_doc=None, selectedModel="gpt-3.5-turbo-16k"
    ):
        """Function that responds to an asked question using open interpreter

        Args:
            conversation : List({role: ... , content: ...})
            from_doc (Doc, optional): Defaults to None.

        Yields:
            chunks of text from the response that are provided as such to achieve
            a tipewriter effect
        """

        prompt = conversation[-1]["content"]
        for coll_name, coll_desc in self.collections.items():
            if self.embedding_db and not coll_desc.startswith("CQN papers"):
                self.embedding_db.load_datasource(coll_name)
                collection_db_response = (
                    f"\n {coll_desc} context: "
                    + self.embedding_db.query(prompt, 3, from_doc)
                )
                prompt += collection_db_response
                print("#### COLLECTION DB RESPONSE:", collection_db_response)

        print("prompt=", prompt)
        print("conversation=", conversation)
        for chunk in interpreter.chat(prompt, stream=True, display=True):
            yield chunk

        yield {"message": ""}

        # # Ensuring the last message in the conversation is a user's question
        # assert (
        #     conversation[-1]["role"] == "user"
        # ), "The final message in the conversation must be a question from the user."
        # conversation = self.truncate_conversation(conversation)

        # prompt = conversation[-1]["content"]

        # # Querying the database to retrieve relevant documents to the user's question
        # docs = ''
        # for coll_name, coll_desc in self.collections.items():
        #     if self.embedding_db:
        #         self.embedding_db.load_datasource(coll_name)
        #         collection_db_response = f'{coll_desc} context: ' + self.embedding_db.query(prompt, 3, from_doc)
        #         docs += collection_db_response + '\n'
        #         print('#### COLLECTION DB RESPONSE:', collection_db_response)
        # print("\n\n\n--------SYSTEM MESSAGE", self.system_message, len(self.collections), self.collections, self.embedding_db)
        # # Creating a chat completion object with OpenAI API to get the model's response
        # messages = conversation
        # if self.embedding_db and len(self.collections) > 0:
        #     messages = [
        #         {"role": "system", "content": self.system_message.format(docs=docs)}
        #     ] + conversation
        # print(messages, f"Docs: |{docs}|")
        # print('NUMBER OF INPUT TOKENS:', len(tiktoken.get_encoding('cl100k_base').encode(docs)))

        # error = 0
        # # try:
        # interpreter.system_message = interpreter_system_message
        # interpreter.model = 'gpt-4'
        # # interpreter.model = 'gpt-3.5-turbo'
        # # interpreter.messages = conversation[:-1]
        # prompt = conversation[-1]["content"]

        # # For the typewriter effect
        # for chunk in interpreter.chat(prompt, stream=True, display=True):
        #     yield chunk

        # except:
        #     error = 1
        #     yield {"content": """Sorry, I am not able to provide a response.

        #                         One of three things happened:
        #                             - The context you provided was too wide, try to be more concise.
        #                             - The files you uploaded were too large
        #                             - I got disconnected from the server
        #                         """}

    def count_tokens(self, string: str, encoding_name="cl100k_base") -> int:
        """Counting the number of tokens in a string using the specified encoding

        Args:
            string (str):
            encoding_name (str, optional): Defaults to 'cl100k_base'.

        Returns:
            int: number of tokens
        """
        encoding = tiktoken.get_encoding(encoding_name)
        num_tokens = len(encoding.encode(string))
        return num_tokens

    def truncate_conversation(self, conversation, token_limit=10000):
        """Truncates the conversation to fit within the token limit

        Args:
            conversation (List({role: ... , content: ...})): the conversation with the bot
            token_limit (int, optional): Defaults to 10000.

        Returns:
            List({role: ... , content: ...}): the truncated conversation
        """
        tokens = 0
        for i in range(len(conversation) - 1, -1, -1):
            tokens += self.count_tokens(conversation[i]["content"])
            if tokens > token_limit:
                print("reached token limit at index", i)
                return conversation[i + 1 :]
        print("total tokens:", tokens)
        return conversation

    def simple_gpt(self, system_message, user_message):
        """Getting model's response for a simple conversation consisting of a system message and a user message

        Args:
            system_message (str)
            user_message (str)

        Returns:
            string : the first choice of response of the model
        """
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k",
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

    def conversation_gpt(self, system_message, conversation):
        """Getting model's response for a conversation with multiple messages

        Args:
            system_message (str)
            conversation (List({role: ... , content: ...}))

        Returns:
            string : the first choice of response of the model
        """
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k",
            messages=[{"role": "system", "content": system_message}] + conversation,
            temperature=1,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            stream=True,
        )
        return response.choices[0].message.content

    def stream_response_generator(
        self, conversation, from_doc, selectedModel="gpt-3.5-turbo-16k"
    ):
        """Returns the generator that generates the response stream of ChatTutor.

        Args:
            conversation (List({role: ... , content: ...})): the current conversation
            from_doc: specify document if necesary, otherwise set to None
        """

        def generate():
            # This function generates responses to the questions in real-time and yields the response
            # along with the time taken to generate it.
            chunks = ""
            start_time = time.time()
            resp = self.ask_question(conversation, from_doc, selectedModel)
            for chunk in resp:
                chunk_content = ""
                if "content" in chunk:
                    chunk_content = chunk["content"]
                chunks += chunk_content
                chunk_time = time.time() - start_time
                # print(f"data: {json.dumps({'time': chunk_time, 'message': chunk})}\n\n")
                yield f"data: {json.dumps({'time': chunk_time, 'message': chunk})}\n\n"

        return generate

    def stream_interpreter_response_generator(
        self, conversation, from_doc, selectedModel="gpt-3.5-turbo-16k"
    ):
        """Returns the generator that generates the response stream of ChatTutor interpreter.

        Args:
            conversation (List({role: ... , content: ...})): the current conversation
            from_doc: specify document if necesary, otherwise set to None
        """

        def generate():
            # This function generates responses to the questions in real-time and yields the response
            # along with the time taken to generate it.
            chunks = ""
            start_time = time.time()
            resp = self.ask_question_interpreter(conversation, from_doc, selectedModel)
            for chunk in resp:
                chunk_content = ""
                if "executing" in chunk:
                    chunk_content = str(chunk["executing"]["code"])
                if "code" in chunk:
                    chunk_content = str(chunk["code"])
                if "output" in chunk:
                    chunk_content = str(chunk["output"])
                chunks += chunk_content
                chunk_time = time.time() - start_time
                print(f"data: {json.dumps({'time': chunk_time, 'message': chunk})}\n\n")
                yield f"data: {json.dumps({'time': chunk_time, 'message': chunk})}\n\n"

        return generate
