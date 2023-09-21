import json
import os
from time import sleep

with open('./keys.json') as f:
    keys = json.load(f)

os.environ['OPENAI_API_KEY'] = keys["lab_openai"]
os.environ['ACTIVELOOP_TOKEN'] = keys["activeloop"]

from reader import read_folder
from database import VectorDatabase

texts = read_folder("./ChatTutor/datasets/62410_content")

print(texts)

database = VectorDatabase("./db", "deeplake_vectordb")
database.init_db()
database.load_datasource("QuantumSystems")

first_half = len(texts) // 2

print('adding first texts')
database.add_texts(texts[:first_half])

sleep(61)

print('adding second half')
database.add_texts(texts[first_half:])

#Collections
#lego_paper - lego paper
#test_notebooks - optics basics, qiskit prelab, and qkd notebooks
#62410_content - all notebooks on the 6.2410 site