from definitions import Doc, Text
from typing import List
import os
import json
from google.cloud import storage

def read_folder_gcp(bucket_name, folder_name):
    """
    Reads the contents of a folder in a GCS bucket and parses each file according to its type, 
    whether pdf, notebook, or plain text.
    
    Parameters:
    - bucket_name: str, Name of the Google Cloud Storage bucket.
    - folder_name: str, Name of the folder in the bucket.
        
    Returns:
        [Text]: an array of texts obtained from parsing the bucket's files.
    """
    texts = []
    
    # Initializing a storage client
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    
    # Iterating through blobs in the specified folder of the bucket
    blobs = bucket.list_blobs(prefix=folder_name)
    blobs_list = list(blobs)
    for blob in blobs_list[:5]:
        # Check if the blob is not the folder itself
        if blob.name != folder_name:
            file_contents = blob.download_as_text()
            doc = Doc(docname=blob.name, citation="", dockey=blob.name)
            
            try:
                if blob.name.endswith(".pdf"): new_texts = parse_pdf(file_contents, doc, 2000, 100)
                elif blob.name.endswith(".ipynb"): new_texts = parse_notebook(file_contents, doc, 2000, 100)
                else: new_texts = parse_plaintext(file_contents, doc, 2000, 100)
                
                texts.extend(new_texts)
            except Exception as e: 
                print(e.__str__())
                pass
                
    return texts

def read_folder(path):
    """
        Reads the contents of a folder and parses each file according to it's type, 
        weather pdf, notebook or plain text. 
        
        Returns:
            [Text]: an array of texts obtained from parsing the folder's files (see definitions.py)
    """
    texts = []

    for dirpath, dirnames, filenames in os.walk(path):
        for file in filenames:
            filepath = os.path.join(dirpath, file)
            doc = Doc(docname=file, citation="", dockey=file)
            try:
                if file.endswith(".pdf"): new_texts = parse_pdf(filepath, doc, 2000, 100)
                elif file.endswith(".ipynb"): new_texts = parse_notebook(filepath, doc, 2000, 100)
                else: new_texts = parse_plaintext(filepath, doc, 2000, 100)
                
                texts.extend(new_texts)
            except Exception as e: 
                print(e.__str__())
                pass
                
    return texts

def parse_plaintext(path: str, doc: Doc, chunk_chars: int, overlap: int):
    """Parses a plain text file and generates texts from its content.

    Args:
        path (str): path to the file
        doc (Doc): Doc object that the Text objects will comply to
        chunk_chars (int): size of chunks
        overlap (int): overlap of chunks

    Returns:
        [Text]: The resulting Texts as an array
    """
    with open(path, "r") as f:
        return texts_from_str(f.read(), doc, chunk_chars, overlap)
    
def parse_notebook(path: str, doc: Doc, chunk_chars: int, overlap: int):
    """Parses a jupyter notebook file and generates texts from its content.

    Args:
        path (str): path to the file
        doc (Doc): Doc object that the Text objects will comply to
        chunk_chars (int): size of chunks
        overlap (int): overlap of chunks

    Returns:
        List(Text): The resulting Texts as an array
    """
    print("parsing notebook ", path)

    with open(path, "r") as f:
        text_str = ""
        data = json.load(f)
        for cell in data["cells"]:
            type = cell["cell_type"]
            if type == "code" or type == "markdown":
                text_str += "".join(cell["source"])

        return texts_from_str(text_str, doc, chunk_chars, overlap)

def parse_pdf(path: str, doc: Doc, chunk_chars: int, overlap: int) -> List[Text]:
    """Parses a pdf file and generates texts from its content.

    Args:
        path (str): path to the file
        doc (Doc): Doc object that the Text objects will comply to
        chunk_chars (int): size of chunks
        overlap (int): overlap of chunks

    Returns:
        List(Text): The resulting Texts as an array
    """
    import pypdf

    pdfFileObj = open(path, "rb")
    pdfReader = pypdf.PdfReader(pdfFileObj)
    split = ""
    pages: List[str] = []
    texts: List[Text] = []
    for i, page in enumerate(pdfReader.pages):
        split += page.extract_text()
        pages.append(str(i + 1))

        while len(split) > chunk_chars:
            # pretty formatting of pages (e.g. 1-3, 4, 5-7)
            pg = "-".join([pages[0], pages[-1]])

            print(split[:chunk_chars])

            texts.append(
                Text(
                    text=split[:chunk_chars], name=f"{doc.docname} pages {pg}", doc=doc
                )
            )
            split = split[chunk_chars - overlap :]
            pages = [str(i + 1)]
    if len(split) > overlap:
        pg = "-".join([pages[0], pages[-1]])
        texts.append(
            Text(text=split[:chunk_chars], name=f"{doc.docname} pages {pg}", doc=doc)
        )
    pdfFileObj.close()
    return texts

def texts_from_str(text_str: str, doc: Doc, chunk_chars: int, overlap: int):
    texts = []
    index = 0
    
    while len(text_str) > chunk_chars:
        texts.append(
            Text(
                text=text_str[:chunk_chars], name=f"{doc.docname} chunk {index}", doc=doc
            )
        )
        index += 1
        text_str = text_str[chunk_chars - overlap :]

    if len(text_str) > overlap:
        texts.append(
            Text(text=text_str[:chunk_chars], name=f"{doc.docname} pages {index}", doc=doc)
        )
    return texts