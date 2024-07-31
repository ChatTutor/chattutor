import re
from nltk.stem import LancasterStemmer
import nltk
from nltk.corpus import words
from nltk.tokenize import word_tokenize
from nltk.metrics import edit_distance

word_list = None
# Load the list of words from the NLTK corpus
try:
    word_list = set(words.words())
except:
    nltk.download("words")
    word_list = set(words.words())


stop_words = [
    "a     ",
    " about ",
    " an    ",
    " are   ",
    " as    ",
    " at    ",
    " be    ",
    " by    ",
    " com   ",
    " de    ",
    " en    ",
    " for   ",
    " from  ",
    " how   ",
    " i     ",
    " in    ",
    " is    ",
    " it    ",
    " la    ",
    " of    ",
    " on    ",
    " or    ",
    " that  ",
    " the   ",
    " this  ",
    " to    ",
    " was   ",
    " what  ",
    " when  ",
    " where ",
    " who   ",
    " will  ",
    " with  ",
    " und   ",
    " the   ",
    " www ",
]

stop_words = [s.strip() for s in stop_words]


def correct_word(word):
    # If the word is already correct, return it
    if word in word_list:
        return word

    # Otherwise, find the closest match based on edit distance
    closest_word = min(word_list, key=lambda w: edit_distance(word, w))
    return closest_word


def longest_common_prefix(strs):
    if not strs:
        return ""

    # Start with the first string as the base prefix
    prefix = strs[0]

    # Compare the prefix with each string in the list
    for string in strs[1:]:
        # Shorten the prefix until it matches the start of the string
        while string[: len(prefix)] != prefix and prefix:
            prefix = prefix[:-1]
        # If the prefix becomes empty, there is no common prefix
        if not prefix:
            return ""
    return prefix


def correct_text(text):
    # Tokenize the text
    tokens = word_tokenize(text)
    # Correct each word
    corrected_tokens = [correct_word(token) for token in tokens]
    # Join corrected tokens into a string
    corrected_text = " ".join(corrected_tokens)
    return corrected_text


def to_sql_match(query):
    query_arr = re.split(r"[- ]+", query.strip())
    words = [s for s in query_arr if s.strip()]
    words = [s for s in words if len(s) > 3]
    words = [s for s in words if not s in stop_words]
    # words = [correct_word(s) for s in words]
    lancaster_stemmer = LancasterStemmer()
    lancaster_stems = [lancaster_stemmer.stem(word) for word in words]
    print("Lancaster Stemmer:", lancaster_stems, "\n", words)
    lancaster_stems = [
        longest_common_prefix([w.lower(), s.lower()]) for (w, s) in zip(words, lancaster_stems)
    ]
    print(lancaster_stems)
    return " ".join("+" + w + "*" for w in lancaster_stems)


if __name__ == "__main__":
    print(to_sql_match("quantum state heralding"))
