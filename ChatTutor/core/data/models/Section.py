from typing import Deque, List, Optional, Tuple
from sqlmodel import Field, Session, SQLModel, create_engine
import uuid as uuid_pkg
from datetime import datetime
from sqlalchemy import Field
from sqlmodel import Field, Relationship
from core.data.models.Course import Course
from core.data.models.SectionCourseLink import SectionCourseLink
class Section(SQLModel, table=True):
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
    section_id: uuid_pkg.UUID = Field(
        default_factory=uuid_pkg.uuid4,
        primary_key=True,
        index=True,
        nullable=False,
    )
    pulling_from : str
    sectionurl : str
    courses: List[Course] = Relationship(back_populates="sections", link_model=SectionCourseLink)
