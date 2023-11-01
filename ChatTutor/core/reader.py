from core.definitions import Doc, Text
from typing import List
import os
import json
from google.cloud import storage
from io import BytesIO
import PyPDF2
from core.vectordatabase import VectorDatabase
from core.url_reader import URLReader
import requests
from requests import Timeout
import time
import shutil

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

    database = VectorDatabase("./db", "chroma")
    database.init_db()
    database.load_datasource("test_embedding")
    # print('bucket:',bucket)

    # Iterating through blobs in the specified folder of the bucket
    blobs = bucket.list_blobs(prefix="")
    # print('blobs:',blobs)
    blobs_list = list(blobs)
    for i, blob in enumerate(blobs_list[::-1]):
        print("on text #" + str(i))
        # print('blob:',blob.name)
        # Check if the blob is not the folder itself
        if blob.name != folder_name:
            file_contents = blob.download_as_bytes()
            doc = Doc(docname=blob.name, citation="", dockey=blob.name)

            try:
                if blob.name.endswith(".pdf"):
                    new_texts = parse_pdf(database, file_contents, doc, 2000, 100)
                elif blob.name.endswith(".ipynb"):
                    new_texts = parse_notebook(file_contents, doc, 2000, 100)
                else:
                    new_texts = parse_plaintext(file_contents, doc, 2000, 100)

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
                if file.endswith(".pdf"):
                    new_texts = parse_pdf(filepath, doc, 2000, 100)
                elif file.endswith(".ipynb"):
                    new_texts = parse_notebook(filepath, doc, 2000, 100)
                else:
                    new_texts = parse_plaintext(filepath, doc, 2000, 100)

                texts.extend(new_texts)
            except Exception as e:
                print(e.__str__())
                pass

    return texts


def read_filearray(files):
    texts = []

    for file in files:
        print("AAAAAAA")
        doc = Doc(docname=file[1], citation="", dockey=file[1])
        print(file[1])
        try:
            if file[1].endswith(".pdf"):
                new_texts = parse_pdf(file[0], doc, 2000, 100)
            elif file[1].endswith(".ipynb"):
                new_texts = parse_notebook_file(file[0], doc, 2000, 100)
            else:
                new_texts = parse_plaintext_file(file[0], doc, 2000, 100)

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

def mathpix_api_call(file):
    options = {
        "conversion_formats": {"docx": False, "tex.zip": True},
        "math_inline_delimiters": ["$", "$"],
        "rm_spaces": True
    }

    head = {
        "app_id": "axiomaticai_d58508",
        "app_key": "4fab240b627e9f59d9303e7dab76aa52283244fee98b37f451125343a8c67325"
    }

    # print(file)

    # Send
    r = requests.post("https://api.mathpix.com/v3/pdf",
                      headers=head,
                      data={
                          "options_json": json.dumps(options)
                      },
                      files={
                          "file": open(file, "rb")
                      }
                      )
    pdf_id = json.loads(r.content).get('pdf_id')
    print('Mathpix submission successful, PDF_id:' + pdf_id)
    # Code is going to ping the server until the file is ready.
    response = ''
    url = "https://api.mathpix.com/v3/pdf/" + pdf_id + ".tex"
    timeout_seconds = 3
    max_retries = 100
    for attempt in range(1, max_retries + 1):
        try:
            response = requests.get(url, headers=head, timeout=timeout_seconds)
            print(response)
            # Check if the request was successful (status code 200)
            if response.status_code == 200:
                # Process the response or save it to a file as needed
                print(f"Request successful on attempt {attempt}")
                break  # Exit the loop if successful
            else:
                print(f"Failed to retrieve the file on attempt {attempt}. Status code: {response.status_code}")
        except Timeout:
            # Handle timeout, optionally you can print a message
            print(f"Request timed out on attempt {attempt}. Retrying...")
        # Introduce a delay before the next attempt, longer for consecutive attempts
        time.sleep(1 + attempt)
    # Make temp folder
    if not os.path.exists('Mathpix/'):
        os.makedirs('Mathpix/')
    # Write tex.zip
    path = 'Mathpix/' + pdf_id + ".tex.zip"
    with open(path, "wb") as f:
        f.write(response.content)
    # Unzip tex.zip
    with zipfile.ZipFile(path) as zf:
        zf.extractall('Mathpix/')
    # Getting text from .tex
    with open('Mathpix/' + pdf_id + '/' + pdf_id + ".tex", 'rb') as f:
        text_str = f.read()
    # Cleanup, not saving images for now
    shutil.rmtree('Mathpix/')

    return text_str


def parse_pdf(file, doc: Doc, chunk_chars: int, overlap: int):
    print('mmmmmmmmmm')

    # Recover PDF through reader. Not ideal, but don't know what the path to the PDF is.
    # Ideally just pass the original PDF path to the API

    pdfReader = PyPDF2.PdfReader(BytesIO(file))

    # Create a new PDF writer
    pdfWriter = PyPDF2.PdfWriter()

    # Iterate through the pages of the original PDF and add them to the new PDF
    for page_num in range(len(pdfReader.pages)):
        page = pdfReader.pages[page_num]  # Use getPage method instead of pages
        pdfWriter.add_page(page)

    # Create a BytesIO object to store the new PDF
    output_pdf = BytesIO()

    # Write the new PDF to the BytesIO object
    pdfWriter.write(output_pdf)

    # Save the new PDF to a file
    with open("mathpix_send.pdf", "wb") as output_file:
        print('Pdf recovered')
        output_file.write(output_pdf.getvalue())

    # API call
    text_str = mathpix_api_call("mathpix_send.pdf")

    # Cleanup
    os.remove("mathpix_send.pdf")

    # Overlaps
    texts = texts_from_str(text_str, doc, chunk_chars, overlap)

    return texts

# def parse_pdf(
#     file_contents: str, doc: Doc, chunk_chars: int, overlap: int
# ) -> List[Text]:
#     """Parses a pdf file and generates texts from its content.
#
#     Args:
#         path (str): path to the file
#         doc (Doc): Doc object that the Text objects will comply to
#         chunk_chars (int): size of chunks
#         overlap (int): overlap of chunks
#
#     Returns:
#         List(Text): The resulting Texts as an array
#     """
#
#     # pdfFileObj = open(path, "rb")
#     pdfReader = PyPDF2.PdfReader(BytesIO(file_contents))
#     # pdfReader = PyPDF2.PdfReader(file_contents)
#     split = ""
#     pages: List[str] = []
#     texts: List[Text] = []
#     for i, page in enumerate(pdfReader.pages):
#         split += page.extract_text()
#         pages.append(str(i + 1))
#
#         while len(split) > chunk_chars:
#             # pretty formatting of pages (e.g. 1-3, 4, 5-7)
#             pg = "-".join([pages[0], pages[-1]])
#
#             # print(split[:chunk_chars])
#             text = [
#                 Text(
#                     text=split[:chunk_chars], name=f"{doc.docname} pages {pg}", doc=doc
#                 )
#             ]
#             # database.add_texts_chroma(text)
#             texts.append(text[0])
#             split = split[chunk_chars - overlap :]
#             pages = [str(i + 1)]
#     if len(split) > overlap:
#         pg = "-".join([pages[0], pages[-1]])
#         texts.append(
#             Text(text=split[:chunk_chars], name=f"{doc.docname} pages {pg}", doc=doc)
#         )
#     # pdfFileObj.close()
#     return texts


def parse_plaintext_file(file, doc: Doc, chunk_chars: int, overlap: int):
    """Parses a plain text file and generates texts from its content.

    Args:
        file: File
        doc (Doc): Doc object that the Text objects will comply to
        chunk_chars (int): size of chunks
        overlap (int): overlap of chunks

    Returns:
        [Text]: The resulting Texts as an array
    """
    print('qqqqqqqqq', file)
    texts = texts_from_str(file, doc, chunk_chars, overlap)
    print(texts)
    # print(texts)
    return texts


def parse_notebook_file(file, doc: Doc, chunk_chars: int, overlap: int):
    """Parses a jupyter notebook file and generates texts from its content.

    Args:
        file: File
        doc (Doc): Doc object that the Text objects will comply to
        chunk_chars (int): size of chunks
        overlap (int): overlap of chunks

    Returns:
        List(Text): The resulting Texts as an array
    """
    text_str = ""
    data = json.load(file)
    for cell in data["cells"]:
        type = cell["cell_type"]
        if type == "code" or type == "markdown":
            text_str += "".join(cell["source"])

    return texts_from_str(text_str, doc, chunk_chars, overlap)


def texts_from_str(text_str: str, doc: Doc, chunk_chars: int, overlap: int):
    texts = []
    index = 0

    if len(text_str) <= chunk_chars and len(text_str) < overlap:
        texts.append(
            Text(
                text=text_str,
                name=f"{doc.docname} chunk {index}",
                doc=doc,
            )
        )
        return texts

    while len(text_str) > chunk_chars:
        texts.append(
            Text(
                text=text_str[:chunk_chars],
                name=f"{doc.docname} chunk {index}",
                doc=doc,
            )
        )
        index += 1
        text_str = text_str[chunk_chars - overlap :]

    if len(text_str) > overlap:
        texts.append(
            Text(
                text=text_str[:chunk_chars],
                name=f"{doc.docname} pages {index}",
                doc=doc,
            )
        )
    return texts


import zipfile


def extract_zip(file):
    """Extracts the content of a zip file and returns file-like objects

    Args:
        file : Zip-file
    Returns: Array of tuples [(file, filename)]
    """
    file_like_object = file.stream._file
    zipfile_ob = zipfile.ZipFile(file_like_object)
    file_names = zipfile_ob.namelist()
    files = [(zipfile_ob.open(name).read(), name) for name in file_names]
    return files


def extract_file(file):
    """Extracts the content of a file and returns file-like objects

    Args:
        file : Zip-file/single-file (pdf, txt of ipynb)
    Returns: Array of tuples [(file, filename)]
    """
    if file.filename.endswith((".pdf", ".txt", ".ipynb")):
        return [(file.read(), file.filename)]
    return extract_zip(file)
