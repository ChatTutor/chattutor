import openai
import tiktoken
import time
import json


class Tutor:
    system_message = """
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

    def __init__(self, embedding_db):
        self.embedding_db = embedding_db

    def ask_question(self, conversation, from_doc=None):
        """Function that responds to an asked question based
        on the current database
        
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
        docs = None
        if self.embedding_db:
            docs = self.embedding_db.query(prompt, 6, from_doc)
        print('DATABASE RESPONSE:', docs)

        # Creating a chat completion object with OpenAI API to get the model's response
        messages = conversation
        if self.embedding_db:
            messages = [
                {"role": "system", "content": self.system_message.format(docs=docs)}
            ] + conversation
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k",
            messages=messages,
            temperature=1,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            stream=True,
        )

        # For the typewriter effect
        for chunk in response:
            yield chunk["choices"][0]["delta"]

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

    def stream_response_generator(self, conversation, from_doc):
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
            for chunk in self.ask_question(conversation, from_doc):
                chunk_content = ""
                if "content" in chunk:
                    chunk_content = chunk["content"]
                chunks += chunk_content
                chunk_time = time.time() - start_time
                yield f"data: {json.dumps({'time': chunk_time, 'message': chunk})}\n\n"

        return generate
