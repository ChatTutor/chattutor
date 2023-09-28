from typing import Any
from pydantic import BaseModel

DocKey = Any

class Doc(BaseModel):
    docname: str
    citation: str
    dockey: DocKey

class Text(BaseModel):
    text: str
    doc: Doc