"""
    Defines which database is used. One can choose between chroma and deeplake
"""

from vectordatabase import VectorDatabase

db = VectorDatabase("34.123.154.72:8000", "chroma", hosted=True)
user_db = VectorDatabase("34.123.154.72:8000", "chroma", hosted=True)

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
