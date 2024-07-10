from typing import Optional
from sqlmodel import Field, Session, SQLModel, create_engine
import uuid as uuid_pkg
from datetime import datetime
from sqlmodel import Field
from dataclasses import dataclass


@dataclass
class AccessCodeModel(SQLModel, table=True):
    """User <-> Course Link (MtoM)

    Columns:
        - username (str): foreign_key "user.username" - username of user
        - course_id (UUID): foreign_key "course.course_id" - id of section

    Args:
        SQLModel (SQLModel): SQLModel
        table (bool, optional): Defaults to True.
    """

    id: str = Field(primary_key=True, index=True)
    code: str = ""
    email: str = Field(unique=True)
    timestamp: datetime = Field(default_factory=datetime.now)

    def jsonserialize(self):
        d = self.__dict__
        d["_sa_instance_state"] = None
        return d