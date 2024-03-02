import tiktoken
from copy import deepcopy


def yield_docs_and_first_sentence_if_tutor_id_not_apologizing(first_sentence: str, valid_docs=list):
    # TODO: replace is_tutor_apologizing_or_thanking by a simple questions to simple_gpt in order to know if the answer was related to a paper?
    # we would need more than the first sentence, and also it might take additional precious time.
    if not is_tutor_apologizing_or_thanking(first_sentence):
        yield {"content": "", "valid_docs": valid_docs}
    else:
        yield {"content": "", "valid_docs": []}

    yield {"role": "assistant", "content": ""}
    for word in first_sentence.split(" "):
        yield {"content": rf" {word}"}


def truncate_to_x_number_of_tokens(string, num_of_tokens=None):
    if num_of_tokens == None or num_of_tokens == 0:
        return string
    cut_string = ""
    string = string.split(" ")
    current_num_of_tokens = 0
    while current_num_of_tokens < num_of_tokens:
        if not string:
            break
        current_num_of_tokens = get_number_of_tokens(cut_string)
        cut_string += " " + string.pop(0)
    return cut_string


def remove_score_and_doc_from_valid_docs(valid_docs):
    # keep only relevant information
    new_valid_docs = []
    for valid_doc in valid_docs:
        new_valid_doc = deepcopy(valid_doc)
        new_valid_doc["doc"] = ""
        new_valid_doc["distance"] = ""
        if new_valid_doc not in new_valid_docs:
            new_valid_docs.append(new_valid_doc)
    valid_docs = new_valid_docs
    return new_valid_docs


def get_number_of_tokens(string):
    return len(tiktoken.get_encoding("cl100k_base").encode(str(string)))


def is_tutor_apologizing_or_thanking(sentence: str):
    import re

    sentence = re.sub("\(.+\)", "", sentence)
    apologizing_thanking_sentences_starts = [
        "i apologize",
        "i am sorry",
        "i'm sorry",
        "great! if you",  # for answers to prompts like "ok, thanks"
        "You're welcome",
        "You are welcome",
    ]

    apologizing_thanking_sentences_starts = [
        el.lower().strip() for el in apologizing_thanking_sentences_starts
    ]
    sentence = sentence.strip().lower()

    for apologizing_thanking_sentences_start in apologizing_thanking_sentences_starts:
        if sentence.startswith(apologizing_thanking_sentences_start):
            return True

    return False
