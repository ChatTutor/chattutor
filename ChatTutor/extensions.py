"""
    Defines which database is used. One can choose between chroma and deeplake
"""

from database import VectorDatabase

db = VectorDatabase("34.123.154.72:8000", 'chroma', hosted=True)

import random
import string

def get_random_string(length):
    # choose from all lowercase letter
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    print("Random string of length", length, "is:", result_str)
    return result_str