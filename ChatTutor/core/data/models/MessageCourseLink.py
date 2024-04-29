from typing import Optional
from sqlmodel import Field, Session, SQLModel, create_engine
import uuid as uuid_pkg
from datetime import datetime
from sqlmodel import Field
from dataclasses import dataclass


@dataclass
class MessageCourseLink(SQLModel, table=True):
    """Section <-> Course Link (MtoM)

    Columns:
        - section_id (UUID): foreign_key "section.section_id" - id of course
        - course_id (UUID): foreign_key "course.course_id" - id of section

    Args:
        SQLModel (SQLModel): SQLModel
        table (bool, optional): Defaults to True.
    """

    message_id: str = Field(foreign_key="message.mes_id", primary_key=True)
    course_id: str = Field(foreign_key="course.course_id", primary_key=True)

    def jsonserialize(self):
        d = self.__dict__
        d["_sa_instance_state"] = None
        return d
