"""
    Program that adds texts read from the `datasets/` forlder using `reader.py`'s 
    `read_folder` function to the `./db` chroma VectorDatabase (see `database.py`)
"""

import json
import os
from time import sleep


with open('./keys.json') as f:
    keys = json.load(f)

os.environ['OPENAI_API_KEY'] = keys["lab_openai"]
os.environ['ACTIVELOOP_TOKEN'] = keys["activeloop"]

from reader import read_folder
from database import VectorDatabase

texts = read_folder("datasets/")

database = VectorDatabase("./db", "chroma")
database.init_db()
database.load_datasource('test_embedding')

# Dividing the texts into two halves
first_half = len(texts) // 2

print('adding first texts')
# Adding the first half of texts to the database
database.add_texts(texts[:first_half])

# Sleeping for 61 seconds to avoid potential rate limiting or other restrictions???
sleep(61)

print('adding second half')
# Adding the second half of texts to the database
database.add_texts(texts[first_half:])

# OLD: Collections information
# lego_paper - contains lego paper
# test_notebooks - contains optics basics, qiskit prelab, and qkd notebooks
# 62410_content - contains all notebooks on the 6.2410 site
