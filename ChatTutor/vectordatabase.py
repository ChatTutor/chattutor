import chromadb
from chromadb.utils import embedding_functions
from typing import List
from definitions import Text
from deeplake.core.vectorstore import VectorStore
import openai
import requests
import json
import os

# Setting up user and URL for activeloop
username = "mit.quantum.ai"
activeloop_url = "https://app.activeloop.ai/api/query/v1"


def embedding_function(texts, model="text-embedding-ada-002"):
    """Function to generate embeddings for given texts using OpenAI API

    Args:
        texts (List(Text)): texts to generate embeddings for
        model (str, optional): Model to use. Defaults to "text-embedding-ada-002".

    Returns:
        embeddings of the texts
    """
    if isinstance(texts, str):
        texts = [texts]
    texts = [t.replace("\n", " ") for t in texts]
    return [
        data["embedding"]
        for data in openai.Embedding.create(input=texts, model=model)["data"]
    ]


# Loading API keys from .env.yaml
if "CHATUTOR_GCP" in os.environ:
    openai.api_key = os.environ["OPENAI_API_KEY"]
else:
    import yaml

    with open(".env.yaml") as f:
        yamlenv = yaml.safe_load(f)
    keys = yamlenv["env_variables"]
    print(keys)
    os.environ["OPENAI_API_KEY"] = keys["OPENAI_API_KEY"]
    os.environ["ACTIVELOOP_TOKEN"] = keys["ACTIVELOOP_TOKEN"]


class VectorDatabase:
    """
    Object that aids the loading, updating and adding of data to
    a database using one of two providers: `chroma` or `deeplake`.

    Attributes
    ----------
    path : str
        path of the folder containing the database
    db_provider : str
        provider of the database: either \'chroma\' or \'deeplake\'
    """

    def __init__(self, path, db_provider, hosted=True):
        self.path = path
        self.hosted = hosted
        self.db_provider = db_provider

    def init_db(self):
        """Initializing the database client if the provider is 'chroma'"""
        if self.db_provider != "chroma":
            return
        # self.client = chromadb.HttpClient(host='34.123.154.72', port=8000)
        if self.hosted:
            ip = self.path.split(":")[0]
            port = int(self.path.split(":")[1])
            self.client = chromadb.HttpClient(host=ip, port=port)
        else:
            self.client = chromadb.PersistentClient(path=self.path)

    def load_datasource(self, name):
        """Loading the appropriate data source based on the database provider"""
        if self.db_provider == "chroma":
            self.load_datasource_chroma(name)
        elif self.db_provider == "deeplake_vectordb":
            self.load_datasource_deeplake(name)
        elif self.db_provider == "deeplake_tensordb":
            self.collection_name = name
        else:
            raise Exception("db_provider must be one of 'chroma' or 'deeplake'")

    def load_datasource_chroma(self, collection_name):
        """Initialize the datasource attribute for the chroma provided VectorDatabase object"""
        openai_ef = embedding_functions.OpenAIEmbeddingFunction(
            model_name="text-embedding-ada-002"
        )
        self.datasource = self.client.get_or_create_collection(
            name=collection_name, embedding_function=openai_ef
        )

    def load_datasource_deeplake(self, dataset_name):
        """Initialize the datasource attribute for the deeplake provided VectorDatabase object"""
        self.datasource = VectorStore(
            path=f"hub://{username}/{dataset_name}", runtime={"tensor_db": True}
        )

    def delete_datasource_chroma(self, collection_name):
        collections = self.client.list_collections()
        coll_names = [coll.name for coll in collections]
        print(coll_names, collection_name)
        if collection_name in coll_names:
            self.client.delete_collection(name=collection_name)
            coll_names = [coll.name for coll in collections]
            print(coll_names, collection_name)

    def add_texts(self, texts: List[Text]):
        """Adding texts to the database based on the database provider

        Args:
            texts (List[Text]) : Texts to add to database
        """
        if self.db_provider == "chroma":
            self.add_texts_chroma(texts)
        elif self.db_provider.startswith("deeplake"):
            self.add_texts_deeplake(texts)
        else:
            raise Exception("db_provider must be one of 'chroma' or 'deeplake'")

    def add_texts_deeplake(self, texts: List[Text]):
        """Adding texts to Deeplake data source with specified embedding function, data, and metadata

        Args:
            texts (List[Text]) : Texts to add to database
        """
        text_strs = [text.text for text in texts]

        self.datasource.add(
            text=text_strs,
            embedding_function=embedding_function,
            embedding_data=text_strs,
            metadata=[{"doc": text.doc.docname} for text in texts],
        )

    def add_texts_chroma(self, texts: List[Text]):
        """Adding texts to Chroma data source with specified ids, metadatas, and documents

        Args:
            texts (List[Text]): Texts to add to database
        """
        count = self.datasource.count()
        ids = [str(i) for i in range(count, count + len(texts))]
        print("ids:", ids)
        print(texts[0].doc.docname)
        self.datasource.add(
            ids=ids,
            metadatas=[{"doc": text.doc.docname} for text in texts],
            documents=[text.text for text in texts],
        )

    def query(self, prompt, n_results, from_doc):
        """Querying the database based on the database provider

        Args:
            prompt (string) : Query for the database
            n_results (int) : Number of results
            from_doc (Doc) : Select only lines where doc = from_doc
        """
        if self.db_provider == "chroma":
            data = self.query_chroma(prompt, n_results, from_doc)
            return " ".join(data["documents"][0])
        elif self.db_provider == "deeplake_vectordb":
            return self.query_deeplake(prompt, n_results, from_doc)
        elif self.db_provider == "deeplake_tensordb":
            return self.query_deeplake_tensor(prompt, n_results, from_doc)
        else:
            raise Exception("db_provider must be one of 'chroma' or 'deeplake'")

    def query_chroma(self, prompt, n_results, from_doc):
        """Querying Chroma data source with specified query_texts, n_results, and optional where clause"""
        if from_doc:
            return self.datasource.query(
                query_texts=prompt, n_results=n_results, where={"doc": from_doc}
            )
        else:
            return self.datasource.query(query_texts=prompt, n_results=6)

    def query_deeplake(self, prompt, n_results, from_doc):
        """Querying Deeplake data source with specified embedding_data, embedding_function, k, optional filter, and exec_option"""
        if from_doc:
            return self.datasource.search(
                embedding_data=prompt,
                embedding_function=embedding_function,
                k=n_results,
                filter={"metadata": {"doc": from_doc}},
                exec_option="compute_engine",
            )
        else:
            return self.datasource.search(
                embedding_data=prompt,
                embedding_function=embedding_function,
                k=n_results,
                exec_option="compute_engine",
            )

    def query_deeplake_tensor(self, prompt, n_results, from_doc):
        """Querying Deeplake tensor data source with specified embedding, query string, and headers"""
        embedding = embedding_function(prompt)
        embedding_string = ",".join(str(item) for item in embedding[0])

        if from_doc != None:
            query_str = f"SELECT * FROM (select text, metadata, COSINE_SIMILARITY(embedding, ARRAY[{embedding_string}]) AS score FROM \"hub://hpstennes/{self.collection_name}\") WHERE metadata['doc'] == '{from_doc}' ORDER BY score desc LIMIT {n_results}"
        else:
            query_str = f'SELECT * FROM (select text, metadata, COSINE_SIMILARITY(embedding, ARRAY[{embedding_string}]) AS score FROM "hub://hpstennes/{self.collection_name}") ORDER BY score desc LIMIT {n_results}'

        response = requests.post(
            activeloop_url,
            json={"query": query_str, "as_list": True},
            headers={"Authorization": "Bearer " + keys["ACTIVELOOP_TOKEN"]},
        )

        print("deeplake response:")
        response_json = json.loads(response.text)
        if "data" in response_json:
            return " ".join([item["text"] for item in response_json["data"]])
        return ""
