from typing import Optional
from sqlmodel import Field, Session, SQLModel, create_engine
import uuid as uuid_pkg
from datetime import datetime
from sqlmodel import Field
from dataclasses import dataclass


@dataclass
class Feedback(SQLModel, table=True):
    """### Feedback Model

    Columns:
        - feedback_id (UUID) : factory generated feedback id
        - message_id (UUID) : foreign_key "message.mes_id"
        - content (str) : content
    Args:
        SQLModel (SQLModel): SQLModel
        table (bool, optional): Defaults to True.
    """

    feedback_id: str = Field(
        default_factory=uuid_pkg.uuid4,
        primary_key=True,
        index=True,
        nullable=False,
    )
    message_id: str = Field(foreign_key="message.mes_id")
    content: str

    def jsonserialize(self):
        d = self.__dict__
        d["_sa_instance_state"] = None
        return d
