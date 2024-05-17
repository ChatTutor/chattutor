from typing import Deque, List, Optional, Tuple
from sqlmodel import Field, Session, SQLModel, create_engine
import uuid as uuid_pkg
from datetime import datetime
from sqlmodel import Field, Relationship
from core.data.models.Course import Course
from core.data.models.SectionCourseLink import SectionCourseLink
from dataclasses import dataclass


@dataclass
class Paper(SQLModel, table=True):
    """### Section Model

    Colums:
        - section_id (UUID): factory generated id
        - pulling_from (str): what documents are available to this section

    Links:
        - courses (List[Course]): courses that have this section

    Args:
        SQLModel (SQLModel): SQLModel
        table (bool, optional): Defaults to True.
    """

    paper_id: str = Field(primary_key=True)
    doc_id: str
    chroma_doc_id: str
    snippet: str
    title: str
    courses: List[Course] = Relationship(back_populates="sections", link_model=SectionCourseLink)
    citations: List[str]

    def jsonserialize(self):
        d = self.__dict__
        d["_sa_instance_state"] = None
        return d
