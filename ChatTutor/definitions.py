from typing import Any
from pydantic import BaseModel

DocKey = Any


class Doc(BaseModel):
    """Doc class that characterizes a paper. It is used
    as an identificator for texts inside the document.

    Attributes:
        docname (str): name of the document
        ciration (str): citation
        dockey (DocKey - Any): dockey

    Args:
        BaseModel
    """

    docname: str
    citation: str
    dockey: DocKey


class Text(BaseModel):
    """Texts from a document that can be added to databases
    or used for embeddings

    Attributes:
        text (str): text
        doc (Doc): document

    Args:
        BaseModel
    """

    text: str
    doc: Doc
