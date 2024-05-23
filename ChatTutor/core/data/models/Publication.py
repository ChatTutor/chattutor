from typing import Deque, List, Optional, Tuple

from sqlalchemy import Column
from sqlmodel import Field, Session, SQLModel, create_engine
import uuid as uuid_pkg
from datetime import datetime
from sqlmodel import Field, Relationship
from sqlalchemy.dialects.mysql import LONGTEXT
from dataclasses import dataclass


@dataclass
class Publication(SQLModel, table=True):
    """DevUser Model

    Columns:
        - username (str): primary_key - username of user
        - email (str): email
        - password (str): hashed pwd of the user
        - user_type (str): type of the user

    Args:
        SQLModel (SQLModel): SQLModel
        table (bool, optional): Defaults to True.
    """

    result_id: str = Field(primary_key=True)
    link: str = Field(sa_column=Column(LONGTEXT))
    chroma_doc_id: str
    # facem cu inner join
    snippet: str = Field(sa_column=Column(LONGTEXT))
    title: str = Field(sa_column=Column(LONGTEXT))
    # authors: List["Author"] = Relationship(back_populates="cqnpublicationmodel", link_model=CQNAuthorLink)
    # citations: List["Citations"] = Relationship(back_populates="cqnpublicationmodel", link_model=CQNCitationLink)

    def jsonserialize(self):
        d = self.__dict__
        d["_sa_instance_state"] = None
        return d
