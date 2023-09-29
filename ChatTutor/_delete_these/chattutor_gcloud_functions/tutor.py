import openai
import tiktoken

# retrieval_prompt = "Use the following pieces of context to answer the users question.\nIf you don't know the answer, just say you don't know, don't try to make up an answer.\n----------------\n{docs}"

system_message = "You are an AI that helps students with questions about a course. Do your best to help the student with their question, using the following helpful context information to inform your response:\n{docs}"

def ask_question(db, conversation, from_doc=None):
    print(conversation)

    assert conversation[-1]["role"] == "user", "The final message in the conversation must be a question from the user."
    conversation = truncate_conversation(conversation)

    print("truncated conversation:")
    print(conversation)

    prompt = conversation[-1]["content"]

    docs = db.query(prompt, 6, from_doc)
    print(docs)

    answer = conversation_gpt(system_message.format(docs=docs), conversation)
    return answer

def count_tokens(string: str, encoding_name='cl100k_base') -> int:
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens

def truncate_conversation(conversation, token_limit=10000):
    tokens = 0
    for i in range(len(conversation) - 1, -1, -1):
        tokens += count_tokens(conversation[i]["content"])
        if tokens > token_limit: 
            print("reached token limit at index", i)
            return conversation[i+1:]
    print("total tokens:", tokens)
    return conversation

def simple_gpt(system_message, user_message):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ],
        temperature=1,
        frequency_penalty=0.0,
        presence_penalty=0.0,
    )
    return response.choices[0].message.content

def conversation_gpt(system_message, conversation):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        messages=[{"role": "system", "content": system_message}] + conversation,
        temperature=1,
        frequency_penalty=0.0,
        presence_penalty=0.0,
    )
    return response.choices[0].message.content
