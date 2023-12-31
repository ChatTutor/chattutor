"""
    Defines which database is used. 
    currenlty, only chroma is suported  
"""

from core.vectordatabase import VectorDatabase

db = VectorDatabase("34.133.39.77:8000", "chroma", hosted=True)
user_db = VectorDatabase("34.133.39.77:8000", "chroma", hosted=True)

import random
import string
from datetime import datetime


def get_random_string(length):
    # choose from all lowercase letter
    letters = string.ascii_lowercase
    result_str = "".join(random.choice(letters) for i in range(length))
    print("Random string of length", length, "is:", result_str)
    return result_str


def generate_unique_name(desc):
    return (
        desc
        + "_"
        + get_random_string(20)
        + datetime.now()
        .isoformat()
        .replace(".", "a")
        .replace(":", "n")
        .replace("-", "d")
    )


def stream_text(text, chunk_size=4, asdict=True):
    def generate():
        i = 0
        d = ""
        for c in text:
            i += 1
            d = d + c
            if i % chunk_size == 0:
                if asdict:
                    yield {"content": d}
                else:
                    yield d
                d = ""

    return generate()
