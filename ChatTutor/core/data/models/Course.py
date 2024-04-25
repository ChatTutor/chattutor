from typing import Deque, List, Optional, Tuple

from sqlmodel import Field, Session, SQLModel, create_engine
import uuid as uuid_pkg
from datetime import datetime
from sqlmodel import Field, Relationship
from core.data.models.SectionCourseLink import SectionCourseLink
from core.data.models.UserCourseLink import UserCourseLink
from core.data.models.StudentCourseLink import StudentCourseLink

from dataclasses import dataclass


@dataclass
class Course(SQLModel, table=True):
    """### Course Model

    Columns:
        - course_id (UUID): factory generated id
        - name (str) : name of course
        - proffessor (Optional[str]) : prof name
        - mainpage (str) : url of mainpage of course
        - collectionname (str) : collection name in chroma db

    Links:
        - sections (List[Section]) : sections 'owned' by this course (e.g. labs/seminars etc) [SectionCourseLink]
        - users (List[User]) : users that own this course [UserCourseLink]

    Args:
        SQLModel (SQLModel): SQLModel
        table (bool, optional): Defaults to True.
    """

    course_id: str = Field(
        default_factory=uuid_pkg.uuid4,
        primary_key=True,
        index=True,
        nullable=False,
    )
    name: str
    proffessor: Optional[str]
    mainpage: str
    collectionname: str
    sections: List["Section"] = Relationship(back_populates="courses", link_model=SectionCourseLink)
    users: List["User"] = Relationship(back_populates="courses", link_model=UserCourseLink)
    students: List["User"] = Relationship(
        back_populates="studied_courses", link_model=StudentCourseLink
    )

    def jsonserialize(self):
        d = self.__dict__
        d["_sa_instance_state"] = None
        return d
