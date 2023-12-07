"""
    Defines which database is used. One can choose between chroma and deeplake
"""

from core.vectordatabase import VectorDatabase
from core.messagedb import MessageDB

db = VectorDatabase("34.133.39.77:8000", "chroma", hosted=True)
user_db = VectorDatabase("34.133.39.77:8000", "chroma", hosted=True)


messageDatabase = MessageDB(
    host="34.41.31.71",
    user="admin",
    password="AltaParolaPuternica1245",
    database="chatmsg",
    statistics_database="sessiondat",
)

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
