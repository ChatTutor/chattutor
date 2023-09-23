import openai
import tiktoken  # Importing tiktoken to count tokens in a string

# The system message provides context to the AI model about its role and how it should respond.
system_message = "You are an AI that helps students with questions about a course. Do your best to help the student with their question, using the following helpful context information to inform your response:\n{docs}"

def ask_question(db, conversation, from_doc=None):
    print(conversation)

    # Ensuring the last message in the conversation is a user's question
    assert conversation[-1]["role"] == "user", "The final message in the conversation must be a question from the user."
    conversation = truncate_conversation(conversation)

    print("truncated conversation:")
    print(conversation)

    prompt = conversation[-1]["content"]

    # Querying the database to retrieve relevant documents to the user's question
    docs = db.query(prompt, 6, from_doc)

    # Creating a chat completion object with OpenAI API to get the model's response
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        messages=[{"role": "system", "content": system_message.format(docs=docs)}] + conversation,
        temperature=1,
        frequency_penalty=0.0,
        presence_penalty=0.0,
        stream=True
    )
    
    # For the typewriter effect
    for chunk in response:
        yield chunk['choices'][0]['delta']


def count_tokens(string: str, encoding_name='cl100k_base') -> int:
    # Counting the number of tokens in a string using the specified encoding
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens

def truncate_conversation(conversation, token_limit=10000):
    # Truncating the conversation to fit within the token limit
    tokens = 0
    for i in range(len(conversation) - 1, -1, -1):
        tokens += count_tokens(conversation[i]["content"])
        if tokens > token_limit: 
            print("reached token limit at index", i)
            return conversation[i+1:]
    print("total tokens:", tokens)
    return conversation

def simple_gpt(system_message, user_message):
    # Getting model's response for a simple conversation consisting of a system message and a user message
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ],
        temperature=1,
        frequency_penalty=0.0,
        presence_penalty=0.0,
        stream=True
    )

    return response.choices[0].message.content

def conversation_gpt(system_message, conversation):
    # Getting model's response for a conversation with multiple messages
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        messages=[{"role": "system", "content": system_message}] + conversation,
        temperature=1,
        frequency_penalty=0.0,
        presence_penalty=0.0,
        stream=True
    )
    return response.choices[0].message.content
