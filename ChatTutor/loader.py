"""
    Program that adds texts read from the `datasets/` forlder using `reader.py`'s 
    `read_folder` function to the `./db` chroma VectorDatabase (see `database.py`)
"""

import json
import os
from google.cloud import storage
import yaml

from reader import read_folder, read_folder_gcp
from database import VectorDatabase

# with open('.env.yaml') as f:
#     yamlenv = yaml.safe_load(f)
# keys = yamlenv["env_variables"]

# os.environ['OPENAI_API_KEY'] = keys["OPENAI_API_KEY"]
# os.environ['ACTIVELOOP_TOKEN'] = keys["ACTIVELOOP_TOKEN"]

# Initializing a storage client
def init_chroma_db():
    storage_client = storage.Client()
    source_bucket_name = 'downloaded_content'
    source_folder_name = './'
    destination_bucket_name = 'chromadb_cqn'
    database_file_name_in_bucket = 'database_file'

    source_bucket = storage_client.bucket(source_bucket_name)

    texts = read_folder_gcp(source_bucket_name, './')

    # Initializing and configuring the database
    database = VectorDatabase("./db", "chroma")
    database.init_db()
    database.load_datasource('test_embedding')

    # Adding texts to the database
    database.add_texts(texts[:5])

    # Let's assume the database is stored in a file named 'database_file' in the './db' directory.
    database_file_path = './db/database_file'

    # Getting the destination bucket object
    destination_bucket = storage_client.bucket(destination_bucket_name)

    # Uploading the database file to the destination bucket
    blob = destination_bucket.blob(database_file_name_in_bucket)
    blob.upload_from_filename(database_file_path)

    print(f'Database file uploaded to {destination_bucket_name}/{database_file_name_in_bucket}')


# Replace 'your-bucket-name' with your actual bucket name and 'your-folder-name' with the name of your folder in the bucket
# texts = read_folder("datasets/")

# database = VectorDatabase("./db", "chroma")
# database.init_db()
# database.load_datasource('test_embedding')

# database.add_texts(texts)


# Dividing the texts into two halves
# first_half = len(texts) // 2

# print('adding first texts')
# Adding the first half of texts to the database
# database.add_texts(texts[:first_half])

# Sleeping for 61 seconds to avoid potential rate limiting or other restrictions???
# sleep(61)

# print('adding second half')
# Adding the second half of texts to the database
# database.add_texts(texts[first_half:])

# OLD: Collections information
# lego_paper - contains lego paper
# test_notebooks - contains optics basics, qiskit prelab, and qkd notebooks
# 62410_content - contains all notebooks on the 6.2410 site
