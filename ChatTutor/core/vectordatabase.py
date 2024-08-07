import os
from threading import Lock
from typing import List

import chromadb
import openai
import google.generativeai as genai
from chromadb.utils import embedding_functions
from core.definitions import Text

# Setting up user
username = "mit.quantum.ai"


def embedding_function(texts, model="text-embedding-ada-002"):
    """
    Function to generate embeddings for given texts using OpenAI API

    Args:
        texts (List(Text)): texts to generate embeddings for
        model (str, optional): Model to use. Defaults to "text-embedding-ada-002".

    Returns:
        embeddings of the texts
    """
    if isinstance(texts, str):
        texts = [texts]
    texts = [t.replace("\n", " ") for t in texts]
    return [data["embedding"] for data in openai.Embedding.create(input=texts, model=model)["data"]]


def embedding_function_gemini(texts, model="models/embedding-001"):
    """
    Function to generate embeddings for given texts using OpenAI API

    Args:
        texts (List(Text)): texts to generate embeddings for
        model (str, optional): Model to use. Defaults to "text-embedding-ada-002".

    Returns:
        embeddings of the texts
    """
    if isinstance(texts, str):
        texts = [texts]
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    genai.configure(api_key=gemini_api_key)

    title = "Custom query"
    return genai.embed_content(
        model=model, content=input, task_type="retrieval_document", title=title
    )["embedding"]


# Loading API keys from .env.yaml
# print('vectordb env variables:', os.environ)
if "CHATTUTOR_GCP" in os.environ or "_CHATUTOR_GCP" in os.environ:
    openai.api_key = os.environ["OPENAI_API_KEY"]
    GOOGLE_API_KEY = os.environ["GEMINI_API_KEY"]
    genai.configure(api_key=GOOGLE_API_KEY)

else:
    import yaml

    with open(".env.yaml") as f:
        yamlenv = yaml.safe_load(f)
    keys = yamlenv["env_variables"]
    GOOGLE_API_KEY = keys["GEMINI_API_KEY"]
    genai.configure(api_key=GOOGLE_API_KEY)
    print(keys)
    os.environ["OPENAI_API_KEY"] = keys["OPENAI_API_KEY"]


class VectorDatabase:
    """
    Object that aids the loading, updating and adding of data to
    a database using one of ~~two~~ providers: `chroma` ~~or `deeplake`~~.

    Attributes
    ----------
    path : str
        path of the folder containing the database
    db_provider : str
        provider of the database: either \'chroma\' or ~~\'deeplake\'~~
    """

    def __init__(self, path, db_provider, hosted=True, ef="openai"):  # TODO: ef = openai
        self.path = path
        self.hosted = hosted
        self.db_provider = db_provider
        self.ef = "openai"

    def init_db(self):
        """
        Initializing the database client if the provider is 'chroma'
        """
        if self.db_provider != "chroma":
            return
        if self.hosted:
            ip = self.path.split(":")[0]
            port = int(self.path.split(":")[1])
            self.client = chromadb.HttpClient(host=ip, port=port)
        else:
            self.client = chromadb.PersistentClient(path=self.path)

    def load_datasource(self, name):
        """
        Loading a collection by it's name:

        Args:
            name (String) - name of the collection. If collection exists
                            it will be loaded, if not, it will be created
                            then loaded"""
        if self.db_provider == "chroma":
            self.load_datasource_chroma(name)
        else:
            raise Exception("db_provider must be one of 'chroma' or 'deeplake'")

    def load_datasource_papers(
        self, collection_name, extra=["titles", "summary", "authors", "citations"]
    ):
        """Load Chroma collection"""
        openai_ef = None

        if self.ef == "openai":
            openai_ef = embedding_functions.OpenAIEmbeddingFunction(
                model_name="text-embedding-ada-002"
            )

        self.datasource = self.client.get_or_create_collection(
            name=collection_name, embedding_function=openai_ef
        )

        self.extra_datasources = {
            x: self.client.get_or_create_collection(
                name=collection_name + "_" + x, embedding_function=openai_ef
            )
            for x in extra
        }

    def load_datasource_chroma(self, collection_name):
        """Load Chroma collection"""
        openai_ef = None

        if self.ef == "openai":
            openai_ef = embedding_functions.OpenAIEmbeddingFunction(
                model_name="text-embedding-ada-002"
            )

        self.datasource = self.client.get_or_create_collection(
            name=collection_name, embedding_function=openai_ef
        )

    def delete_datasource_chroma(self, collection_name):
        """
        Unload and delete Chroma collection
        Please make sure you know what you're doing when using this,
        the operation is ireversible.
        """
        collections = self.client.list_collections()
        coll_names = [coll.name for coll in collections]
        print(coll_names, collection_name)
        if collection_name in coll_names:
            self.client.delete_collection(name=collection_name)
            coll_names = [coll.name for coll in collections]
            print(coll_names, collection_name)

    def add_texts(self, texts: List[Text]):
        """Equivalent to add_texts_chroma

        Args:
            texts (List[Text]) : Texts to add to database
        """
        if self.db_provider == "chroma":
            self.add_texts_chroma(texts)
        else:
            raise Exception("db_provider must be one of 'chroma' or 'deeplake'")

    def add_texts_chroma(self, texts: List[Text]):
        """
        Adding texts to Chroma data source with specified ids, metadatas, and documents

        Args:
            texts (List[Text]): Texts to add to database
        """
        count = self.datasource.count()
        ids = [str(i) for i in range(count, count + len(texts))]
        self.datasource.add(
            ids=ids,
            metadatas=[{"doc": text.doc.docname} for text in texts],
            documents=[text.text for text in texts],
        )

    def add_texts_papers(self, texts: List[Text], variant=None):
        """
        Adding texts to Chroma data source with specified ids, metadatas, and documents

        Args:
            texts (List[Text]): Texts to add to database
        """
        count = self.datasource.count()
        ids = [str(i) for i in range(count, count + len(texts))]
        if variant == None:
            self.datasource.add(
                ids=ids,
                metadatas=[{"doc": text.doc.docname} for text in texts],
                documents=[text.text for text in texts],
            )
        else:
            self.extra_datasources[variant].add(
                ids=ids,
                metadatas=[{"doc": text.doc.docname} for text in texts],
                documents=[text.text for text in texts],
            )

    def add_texts_chroma_lock(self, texts: List[Text], lock: Lock):
        """
        Adding texts to Chroma data source with specified ids, metadatas, and documents,
        for parallel url spidering. This would lock the mutex lock first and then work like
        add_texts_chroma before unlocking it.
        Args:
            texts (List[Text]): Texts to add to database
            lock (Lock): the threading lock
        """
        lock.acquire()
        count = self.datasource.count()
        ids = [str(i) for i in range(count, count + len(texts))]
        # print(ids, count)
        self.datasource.add(
            ids=ids,
            metadatas=[{"doc": text.doc.docname} for text in texts],
            documents=[text.text for text in texts],
        )
        lock.release()

    def query(self, prompt, n_results, from_doc, metadatas=False, distances=False):
        """Equivalent of query_chroma
        Args:
            from_doc (string | list[string]) -  should be either a string  a list of strings
            include (list[string]) - any cmbination of embeddings, documents, metadatas. Defaults to ["documents"]
            prompt - the query text
        """
        if self.db_provider == "chroma":
            print(from_doc)
            data = self.query_chroma(
                prompt,
                n_results=n_results,
                from_doc=from_doc,
                include=["documents", "metadatas", "distances"],
            )
            if metadatas:
                return (
                    data["documents"][0],
                    data["metadatas"][0],
                    data["distances"][0],
                    " ".join(data["documents"][0]),
                )
            return " ".join(data["documents"][0])
        else:
            raise Exception("db_provider must be one of 'chroma' or 'deeplake'")

    def query_papers_m(
        self, prompt, n_results, from_doc, metadatas=False, distances=False, variant=None
    ):
        """Equivalent of query_chroma
        Args:
            from_doc (string | list[string]) -  should be either a string  a list of strings
            include (list[string]) - any cmbination of embeddings, documents, metadatas. Defaults to ["documents"]
            prompt - the query text
        """
        if variant is None:
            if self.db_provider == "chroma":
                print(from_doc)
                data = self.query_chroma(
                    prompt,
                    n_results=n_results,
                    from_doc=from_doc,
                    include=["documents", "metadatas", "distances"],
                )
                if metadatas:
                    return (
                        data["documents"][0],
                        data["metadatas"][0],
                        data["distances"][0],
                        " ".join(data["documents"][0]),
                        data,
                    )
                return " ".join(data["documents"][0]), data
            else:
                raise Exception("db_provider must be one of 'chroma' or 'deeplake'")
        else:
            if self.db_provider == "chroma":
                print(from_doc)
                data = self.query_papers(
                    prompt,
                    n_results=n_results,
                    from_doc=from_doc,
                    include=["documents", "metadatas", "distances"],
                    variant=variant,
                )
                if metadatas:
                    return (
                        data["documents"][0],
                        data["metadatas"][0],
                        data["distances"][0],
                        " ".join(data["documents"][0]),
                        data,
                    )
                return " ".join(data["documents"][0]), data

            else:
                raise Exception("db_provider must be one of 'chroma' or 'deeplake'")

    def query_chroma(self, prompt, n_results, from_doc, include=["documents"]):
        """Querying Chroma data source with specified query text,
        getting best match from the chroma embeddings
        Args:
            from_doc (string | list[string]) -  should be either a string  a list of strings
            include (list[string]) - any cmbination of embeddings, documents, metadatas. Defaults to ["documents"]
            prompt - the query text
        """
        if from_doc:
            if hasattr(from_doc, "__len__") and (not isinstance(from_doc, str)):
                return self.datasource.query(
                    query_texts=prompt,
                    n_results=n_results,
                    where={"doc": {"$in": from_doc}},
                    include=include,
                )
            else:
                return self.datasource.query(
                    query_texts=prompt,
                    n_results=n_results,
                    where={"doc": from_doc},
                    include=include,
                )
        else:
            return self.datasource.query(query_texts=prompt, n_results=n_results, include=include)

    def query_papers(self, prompt, n_results, from_doc, include=["documents"], variant=None):
        """Querying Chroma data source with specified query text,
        getting best match from the chroma embeddings
        Args:
            from_doc (string | list[string]) -  should be either a string  a list of strings
            include (list[string]) - any cmbination of embeddings, documents, metadatas. Defaults to ["documents"]
            prompt - the query text
            variant - the query text
        """
        if variant is None:
            if from_doc:
                if hasattr(from_doc, "__len__") and (not isinstance(from_doc, str)):
                    return self.datasource.query(
                        query_texts=prompt,
                        n_results=n_results,
                        where={"doc": {"$in": from_doc}},
                        include=include,
                    )
                else:
                    return self.datasource.query(
                        query_texts=prompt,
                        n_results=n_results,
                        where={"doc": from_doc},
                        include=include,
                    )
            else:
                return self.datasource.query(
                    query_texts=prompt, n_results=n_results, include=include
                )
        else:
            if from_doc:
                if hasattr(from_doc, "__len__") and (not isinstance(from_doc, str)):
                    return self.extra_datasources[variant].query(
                        query_texts=prompt,
                        n_results=n_results,
                        where={"doc": {"$in": from_doc}},
                        include=include,
                    )
                else:
                    return self.extra_datasources[variant].query(
                        query_texts=prompt,
                        n_results=n_results,
                        where={"doc": from_doc},
                        include=include,
                    )
            else:
                return self.extra_datasources[variant].query(
                    query_texts=prompt, n_results=n_results, include=include
                )

    def get_chroma(self, n_results, from_doc, include=["documents"]):
        """
        Get document from ChromaDB that matches from_doc exactly.
        Args:
            from_doc (string | list[string]) -  should be either a string  a list of strings
            include (list[string]) - any cmbination of embeddings, documents, metadatas. Defaults to ["documents"]
        """
        if from_doc and (type(from_doc) in (list,)):
            return self.datasource.get(
                where={"doc": {"$in": from_doc}},
                include=include,
            )
        elif from_doc:
            return self.datasource.get(
                where={"doc": from_doc},
                include=include,
            )
        else:
            return self.datasource.get(include=include)
