from typing import Deque, List, Optional, Tuple
from sqlmodel import Field, Session, SQLModel, create_engine, Text
import uuid as uuid_pkg
from datetime import datetime
from sqlmodel import Field, Relationship
from dataclasses import dataclass
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy import Column
from core.data.models.MessageCourseLink import MessageCourseLink
from core.data.models.MessageUserLink import MessageUserLink


@dataclass
class Message(SQLModel, table=True):
    """### Message Model

    Columns:
        - role (str) : "assistant" | "user" - who sent the message
        - content (str) : message content
        - chat_key (UUID) : foreign_key "chat.chat_id" - id of the chat the
                        message was sent in
        - clear_number (Optional[int]) : number of clears that happened until message
        - time_created (datetime) : defaults to factoy generated datetime.now
        - credential_token (str) : credential token of user [Not used yet] : TODO

    Args:
        SQLModel (SQLModel): SQLModel
        table (bool, optional): Defaults to True.
    """

    mes_id: str = Field(
        default_factory=uuid_pkg.uuid4,
        primary_key=True,
        index=True,
        nullable=False,
    )
    role: str
    content: str = Column(LONGTEXT)
    chat_key: str = Field(foreign_key="chat.chat_id")
    clear_number: Optional[int]
    time_created: datetime = Field(default_factory=datetime.now)
    credential_token: str
    courses: List["Course"] = Relationship(
        back_populates="messages",
        link_model=MessageCourseLink,
    )
    users: List["User"] = Relationship(
        back_populates="messages",
        link_model=MessageUserLink,
    )

    def jsonserialize(self):
        d = self.__dict__
        d["_sa_instance_state"] = None
        return d

    def jsonserialize_noclear(self):
        d = self.__dict__
        # d["_sa_instance_state"] = None
        return d
