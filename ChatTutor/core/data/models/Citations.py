from typing import Deque, List, Optional, Tuple
from sqlmodel import Field, Session, SQLModel, create_engine
import uuid as uuid_pkg
from datetime import datetime
from sqlmodel import Field, Relationship

from dataclasses import dataclass


@dataclass
class Citations(SQLModel, table=True):
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

    citation_id: str = Field(primary_key=True)
    snippet: str
    title: str
    cqn_pub_id: str
    # papers: List["CQNPublicationModel"] = Relationship(
    #     back_populates="citations", link_model=CQNCitationLink
    # )

    def jsonserialize(self):
        d = self.__dict__
        d["_sa_instance_state"] = None
        return d
