from typing import Optional
from sqlmodel import Field, Session, SQLModel, create_engine
import uuid as uuid_pkg
from datetime import datetime
from sqlmodel import Field
from dataclasses import dataclass

@dataclass
class Chat(SQLModel, table=True):
    """Chat Model
    
    chat_id (UUID): factory generated id

    Args:
        SQLModel (SQLModel): SQLModel
        table (bool, optional): Defaults to True.
    """
    chat_id: str = Field(
        default_factory=uuid_pkg.uuid4,
        primary_key=True,
        index=True,
        nullable=False
    )
    
    def jsonserialize(self):
        d = self.__dict__
        d["_sa_instance_state"] = None
        return d
