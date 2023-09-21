import chromadb
from chromadb.utils import embedding_functions
from typing import List
from definitions import Text
from deeplake.core.vectorstore import VectorStore
import openai
import requests
import json

username = "hpstennes"
activeloop_url = "https://app.activeloop.ai/api/query/v1"

def embedding_function(texts, model="text-embedding-ada-002"):
    if isinstance(texts, str):
        texts = [texts]
    texts = [t.replace("\n", " ") for t in texts]
    return [data['embedding']for data in openai.Embedding.create(input = texts, model=model)['data']]

with open('./keys.json') as f:
    keys = json.load(f)

class VectorDatabase:

    def __init__(self, path, db_provider):
        self.path = path
        self.db_provider = db_provider

    def init_db(self):
        if self.db_provider != "chroma": return
        self.client = chromadb.PersistentClient(path=self.path)
    
    def load_datasource(self, name):
        if self.db_provider == "chroma":
            self.load_datasource_chroma(name)
        elif self.db_provider == "deeplake_vectordb":
            self.load_datasource_deeplake(name)
        elif self.db_provider == "deeplake_tensordb":
            self.collection_name = name
        else: raise Exception("db_provider must be one of \'chroma\' or \'deeplake\'")

    def load_datasource_chroma(self, collection_name):
        openai_ef = embedding_functions.OpenAIEmbeddingFunction(
            model_name="text-embedding-ada-002"
        )
        self.datasource = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=openai_ef
        )

    def load_datasource_deeplake(self, dataset_name):
        self.datasource = VectorStore(
            path = f"hub://{username}/{dataset_name}",
            runtime = {"tensor_db": True}
        )

    def add_texts(self, texts: List[Text]):
        if self.db_provider == "chroma":
            self.add_texts_chroma(texts)
        elif self.db_provider.startswith("deeplake"):
            self.add_texts_deeplake(texts)
        else: raise Exception("db_provider must be one of \'chroma\' or \'deeplake\'")

    def add_texts_deeplake(self, texts: List[Text]):        
        text_strs = [text.text for text in texts]

        self.datasource.add(text = text_strs, 
            embedding_function = embedding_function, 
            embedding_data = text_strs, 
            metadata = [{"doc": text.doc.docname} for text in texts])

    def add_texts_chroma(self, texts: List[Text]):
        count = self.datasource.count()
        ids = [str(i) for i in range(count, count + len(texts))]
        print(ids)
        self.datasource.add(
            ids=ids,
            metadatas=[{"doc": text.doc.docname} for text in texts],
            documents=[text.text for text in texts]
        )

    def query(self, prompt, n_results, from_doc):
        if self.db_provider == "chroma":
            data = self.query_chroma(prompt, n_results, from_doc)
            return " ".join(data["documents"][0])
        elif self.db_provider == "deeplake_vectordb":
            return self.query_deeplake(prompt, n_results, from_doc)
        elif self.db_provider == "deeplake_tensordb":
            return self.query_deeplake_tensor(prompt, n_results, from_doc)
        else: raise Exception("db_provider must be one of \'chroma\' or \'deeplake\'")
    
    def query_chroma(self, prompt, n_results, from_doc):
        if from_doc:
            return self.datasource.query(query_texts=prompt, n_results=n_results, where={"doc": from_doc})
        else:
            return self.datasource.query(query_texts=prompt, n_results=6)
        
    def query_deeplake(self, prompt, n_results, from_doc):
        if from_doc:
            return self.datasource.search(embedding_data=prompt, embedding_function=embedding_function, k=n_results, 
                                          filter={"metadata": {"doc": from_doc}}, exec_option = "compute_engine")
        else:
            return self.datasource.search(embedding_data=prompt, embedding_function=embedding_function, k=n_results, exec_option = "compute_engine")
        
    def query_deeplake_tensor(self, prompt, n_results, from_doc):
        embedding = embedding_function(prompt)
        embedding_string = ",".join(str(item) for item in embedding[0])
        
        with open('./keys.json') as f:
            keys = json.load(f)

        if from_doc != None:
            query_str = f"SELECT * FROM (select text, metadata, COSINE_SIMILARITY(embedding, ARRAY[{embedding_string}]) AS score FROM \"hub://hpstennes/{self.collection_name}\") WHERE metadata[\'doc\'] == \'{from_doc}\' ORDER BY score desc LIMIT {n_results}"
        else:
            query_str = f"SELECT * FROM (select text, metadata, COSINE_SIMILARITY(embedding, ARRAY[{embedding_string}]) AS score FROM \"hub://hpstennes/{self.collection_name}\") ORDER BY score desc LIMIT {n_results}"

        response = requests.post(activeloop_url, 
            json={
                "query": query_str,
                "as_list": True
            }, 
            headers={
                "Authorization": "Bearer " + keys["activeloop"]
            })

        print("deeplake response:")
        response_json = json.loads(response.text)
        if "data" in response_json:
            return " ".join([item["text"] for item in response_json["data"]])
        return ""