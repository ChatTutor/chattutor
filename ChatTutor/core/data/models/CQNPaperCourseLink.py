from typing import Deque, List, Optional, Tuple
from sqlmodel import Field, Session, SQLModel, create_engine
import uuid as uuid_pkg
from datetime import datetime
from sqlmodel import Field, Relationship
from dataclasses import dataclass


@dataclass
class CQNPaperCourseLink(SQLModel, table=True):
    """User <-> Course Link (MtoM)

    Columns:
        - username (str): foreign_key "user.username" - username of user
        - course_id (UUID): foreign_key "course.course_id" - id of section

    Args:
        SQLModel (SQLModel): SQLModel
        table (bool, optional): Defaults to True.
    """

    course: str = Field(foreign_key="course.course_id", primary_key=True)
    paper_id: str = Field(foreign_key="cqnpublicationmodel.result_id", primary_key=True)

    def jsonserialize(self):
        d = self.__dict__
        d["_sa_instance_state"] = None
        return d