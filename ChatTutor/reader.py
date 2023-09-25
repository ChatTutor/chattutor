from definitions import Doc, Text
from typing import List
import os
import json

def read_folder(path):
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
    with open(path, "r") as f:
        return texts_from_str(f.read(), doc, chunk_chars, overlap)
    
def parse_notebook(path: str, doc: Doc, chunk_chars: int, overlap: int):

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