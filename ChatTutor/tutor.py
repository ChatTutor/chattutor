import openai
import tiktoken
import time
import json
from extensions import stream_text
import interpreter

cqn_system_message = """
    You are embedded into the Center for Quantum Networks (CQN) website as an Interactive Research Assistant. Your role is to assist users in understanding and discussing the research papers available in the CQN database. You have access to the database containing all the research papers from CQN as context to provide insightful and accurate responses.

    - Engage users with polite, concise, and informative replies.
    - Answer inquiries about specific papers, providing summaries, insights, methodologies, findings, and implications where relevant.
    - Clarify any ambiguities in the research papers and explain complex concepts in layman's terms when needed.
    - Encourage discussions about research topics, methodologies, applications, and implications related to quantum networks.
    - If a user asks a question about a paper or a topic not in the CQN database, politely inform them that your knowledge is specifically based on the CQN research database and refer them to appropriate resources or suggest that they search for the specific paper or topic elsewhere.
    - By default, write all math/physics equations and symbols in latex

    Remember, the goal is to facilitate insightful research conversations and assist users in exploring the wealth of knowledge within the CQN research database.
    \n{docs}
    """

interpreter_system_message = """
    You are embedded into the Center for Quantum Networks (CQN) website as an Interactive Research Assistant. Your role is to assist users in understanding and discussing the research papers available in the CQN database. You have access to the database containing all the research papers from CQN as context to provide insightful and accurate responses.

    - Engage users with polite, concise, and informative replies.
    - Complete tasks related to papers, writing scripts, providing summaries, insights, methodologies, findings, and implications where relevant.
    - Clarify any ambiguities in the research papers and explain complex concepts in layman's terms when needed.
    - Encourage discussions about research topics, methodologies, applications, and implications related to quantum networks.
    - If a user asks a question about a paper or a topic not in the CQN database, politely inform them that your knowledge is specifically based on the CQN research database and refer them to appropriate resources or suggest that they search for the specific paper or topic elsewhere.
    - By default, write all math/physics equations and symbols in latex

    Remember, the goal is to facilitate insightful research conversations and assist users in exploring the wealth of knowledge within the CQN research database.
    \n{docs}
    """

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
    def __init__(self, embedding_db, embedding_db_name="CQN database", system_message=default_system_message):
        """ 
            Args:
                embedding_db (VectorDatabase): the db with any or no source loaded 
                embedding_db_name (str): Description of embedding_db.
                system_message (str)

            Return:
                Tutor object with no collections to load from. Use add_collection to add
                collection to load from. 
        """
        self.embedding_db = embedding_db
        self.embedding_db_name = embedding_db_name
        self.collections = {}
        self.system_message = system_message
    
    def add_collection(self, name, desc):
        """Adds a collection to self.collections
            Args:
                name (str): name of the collection to load form the chromadb (embedding_db)
                desc (str): description prompted to the model
        """
        self.collections[name] = desc

    def ask_question(self, conversation, from_doc=None, selectedModel='gpt-3.5-turbo-16k'):
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

        prompt = conversation[-1]["content"]

        # Querying the database to retrieve relevant documents to the user's question
        docs = ''
        for coll_name, coll_desc in self.collections.items():
            if self.embedding_db:
                self.embedding_db.load_datasource(coll_name)
                collection_db_response = f'{coll_desc} context: ' + self.embedding_db.query(prompt, 3, from_doc)
                docs += collection_db_response + '\n'
                print('#### COLLECTION DB RESPONSE:', collection_db_response)
        print("\n\n\n--------SYSTEM MESSAGE", self.system_message, len(self.collections), self.collections, self.embedding_db)
        # Creating a chat completion object with OpenAI API to get the model's response
        messages = conversation
        if self.embedding_db and len(self.collections) > 0:
            messages = [
                {"role": "system", "content": self.system_message.format(docs=docs)}
            ] + conversation
        print(messages, f"Docs: |{docs}|")
        print('NUMBER OF INPUT TOKENS:', len(tiktoken.get_encoding('cl100k_base').encode(docs)))

        error = 0
        try:
            response = openai.ChatCompletion.create(
                model=selectedModel,
                messages=messages,
                temperature=1,
                frequency_penalty=0.0,
                presence_penalty=0.0,
                stream=True,
            )
        

            # For the typewriter effect
            for chunk in response:
                yield chunk["choices"][0]["delta"]
        except:
            error = 1
            yield {"content": """Sorry, I am not able to provide a response. 
                                
                                One of three things happened:
                                    - The context you provided was too wide, try to be more concise.
                                    - The files you uploaded were too large
                                    - I got disconnected from the server
                                """}
            
    def ask_question_interpreter(self, conversation, from_doc=None, selectedModel='gpt-3.5-turbo-16k'):
        """Function that responds to an asked question using open interpreter
        
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

        prompt = conversation[-1]["content"]

        # Querying the database to retrieve relevant documents to the user's question
        docs = ''
        for coll_name, coll_desc in self.collections.items():
            if self.embedding_db:
                self.embedding_db.load_datasource(coll_name)
                collection_db_response = f'{coll_desc} context: ' + self.embedding_db.query(prompt, 3, from_doc)
                docs += collection_db_response + '\n'
                print('#### COLLECTION DB RESPONSE:', collection_db_response)
        print("\n\n\n--------SYSTEM MESSAGE", self.system_message, len(self.collections), self.collections, self.embedding_db)
        # Creating a chat completion object with OpenAI API to get the model's response
        messages = conversation
        if self.embedding_db and len(self.collections) > 0:
            messages = [
                {"role": "system", "content": self.system_message.format(docs=docs)}
            ] + conversation
        print(messages, f"Docs: |{docs}|")
        print('NUMBER OF INPUT TOKENS:', len(tiktoken.get_encoding('cl100k_base').encode(docs)))

        error = 0
        try:
            response = openai.ChatCompletion.create(
                model=selectedModel,
                messages=messages,
                temperature=1,
                frequency_penalty=0.0,
                presence_penalty=0.0,
                stream=True,
            )

            interpreter.system_message = interpreter_system_message
            interpreter.messages = conversation[:-1]
            prompt = conversation[-1]["content"]

            response = interpreter.chat(prompt, stream=True, display=True)
        
            # For the typewriter effect
            for chunk in response:
                yield chunk
        except:
            error = 1
            yield {"content": """Sorry, I am not able to provide a response. 
                                
                                One of three things happened:
                                    - The context you provided was too wide, try to be more concise.
                                    - The files you uploaded were too large
                                    - I got disconnected from the server
                                """}
            
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
            stream=True,
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

    def stream_response_generator(self, conversation, from_doc, selectedModel='gpt-3.5-turbo-16k'):
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
                print(f"data: {json.dumps({'time': chunk_time, 'message': chunk})}\n\n")
                yield f"data: {json.dumps({'time': chunk_time, 'message': chunk})}\n\n"

        return generate
    
    def stream_interpreter_response_generator(self, conversation, from_doc, selectedModel='gpt-3.5-turbo-16k'):
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
                # print('ppppp',chunk)
                chunk_content = ""
                if "message" in chunk:
                    # print('sssssss',chunk["message"])
                    chunk_content = str(chunk["message"])
                if "code" in chunk:
                    # print('qqqqqq',chunk['code'])
                    chunk_content = str(chunk["code"])
                chunks += chunk_content
                chunk_time = time.time() - start_time
                print(f"data: {json.dumps({'time': chunk_time, 'message': chunk})}\n\n")
                yield f"data: {json.dumps({'time': chunk_time, 'message': chunk})}\n\n"

        return generate
