import io
import re

from core.definitions import Doc
from core.extensions import db, generate_unique_name, get_random_string
from core.reader import extract_file, parse_plaintext_file_read, read_filearray
from core.url_spider import URLSpider
from flask import Blueprint, jsonify, request
from werkzeug.datastructures import FileStorage

reader_bp = Blueprint("bp_reader", __name__)


@reader_bp.route("/upload_data_to_process", methods=["POST"])
def upload_data_to_process():
    """
    The function `upload_data_to_process` uploads data from a file, extracts the contents, and adds them
    to a database collection with a generated name.
    URLParams:
        ```
        {
            "file" : list[FormFile]
        }
        ```
    Returns:
        -  a JSON response containing the "collection_name" key. The value of "collection_name" is
    either False if no file was uploaded, or a generated unique name for the collection the file was added to
    if a file was uploaded.

        ```
        {
            "collection_name" : str # collection the file was uploaded to
        }
        ```
    """
    file = request.files.getlist("file")
    print(file)
    data = request.form
    desc = data["name"].replace(" ", "-")
    if len(desc) == 0:
        desc = "untitled" + "-" + get_random_string(5)
    resp = {"collection_name": False}
    print("File,", file)
    if file[0].filename != "":
        files = []
        for f in file:
            files = files + extract_file(f)
            print(f"Extracted file {f}")
        texts = read_filearray(files)
        # Generating the collection name based on the name provided by user, a random string and the current
        # date formatted with punctuation replaced
        collection_name = generate_unique_name(desc)

        db.load_datasource(collection_name)
        db.add_texts(texts)
        resp["collection_name"] = collection_name

    return jsonify(resp)



@reader_bp.route("/upload_data_from_drop", methods=["POST"])
def upload_data_from_drop():
    """
    The function `upload_data_from_drop` uploads data from a file to a database collection, extracts the
    file contents, and adds the extracted texts to the collection.

    URLParams:
        ```
        {
            "file" : list[FormFile],
            "collection_name" : str # collection to add to
        }
        ```
    Returns:
        -  a JSON response containing the "collection_name" key if a file was uploaded.

        ```
        {
            "collection_name" : str # collection the file was uploaded to
            "files_uploaded_name" : list[FormFiles] # uploaded files
        }
        ```
    """
    try:
        cname = request.form.get("collection_name")

        file = request.files.getlist("file")
        print('Uploading: ', file, ' to: ', cname)
        f_arr = []
        for fil in file:
            f_arr.append(fil.filename)

        resp = {"collection_name": cname, "files_uploaded_name": f_arr}
        if file[0].filename != "":
            files = []
            for f in file:
                files = files + extract_file(f)
                print(f"Extracted file {f}")

            texts = read_filearray(files)
            # Generating the collection name based on the name provided by user, a random string and the current
            # date formatted with punctuation replaced
            print(cname)
            db.load_datasource(cname)
            db.add_texts(texts)

        return jsonify(resp)
    except Exception as e:
        return jsonify({"message": "error"})


@reader_bp.route("/upload_site_url", methods=["POST"])
def upload_site_url():
    """
    The `upload_site_url` function takes a JSON object containing a collection name and a list of URLs,
    parses the content of each URL, and adds the parsed text to a database. It returns a JSON response
    containing the collection name, URLs, and a list of document names that were successfully added to
    the database.

    URLParams:
        ```
        {
            "url" : list[str],
            "name" : str # collection to add to
        }
        ```
    Returns:
        ```
        {
            "collection_name" : str, # collection the urls were uploaded to
            "urls" : list[str], # original urls
            "docs" : list[any], # succesfully uploaded urls
        }
        ```
    """
    try:
        ajson = request.json
        coll_name = ajson["name"]
        url_to_parse = ajson["url"]
        print("UTP: ", url_to_parse)
        collection_name = coll_name
        resp = {"collection_name": coll_name, "urls": url_to_parse, "docs": []}
        for surl in url_to_parse:
            print(surl)
            ss = URLSpider.parse_url(surl)
            site_text = f"{ss.encode('utf-8', errors='replace')}"
            navn = re.sub(r"[^A-Za-z0-9\-_]", "_", surl)
            db.load_datasource(collection_name)
            docs = db.get_chroma(from_doc=navn, n_results=1)
            if docs == None:
                continue
            if len(docs) > 0:
                resp["docs"] = resp["docs"] + [navn + "/_already_exists"]
                continue

            file = FileStorage(stream=io.BytesIO(bytes(site_text, "utf-8")), name=navn)
            f_f = (file, navn)

            doc = Doc(docname=f_f[1], citation="", dockey=f_f[1])
            texts = parse_plaintext_file_read(f_f[0], doc=doc, chunk_chars=2000, overlap=100)
            db.load_datasource(collection_name)
            db.add_texts(texts)
            resp["docs"] = resp["docs"] + [navn]
        return jsonify(resp)
    except Exception as e:
        print(e)
        return jsonify({"message": "error"})
