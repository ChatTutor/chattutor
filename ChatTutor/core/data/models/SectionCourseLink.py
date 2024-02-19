from typing import Optional
from sqlmodel import Field, Session, SQLModel, create_engine
import uuid as uuid_pkg
from datetime import datetime
from sqlalchemy import Field
from sqlmodel import Field

class SectionCourseLink(SQLModel, table=True):
    """Section <-> Course Link (MtoM)
    
    Columns:
        - section_id (UUID): foreign_key "section.section_id" - id of course
        - course_id (UUID): foreign_key "course.course_id" - id of section

    Args:
        SQLModel (SQLModel): SQLModel
        table (bool, optional): Defaults to True.
    """
    section_id: uuid_pkg.UUID = Field(foreign_key="section.section_id", primary_key=True)
    course_id: uuid_pkg.UUID = Field(foreign_key="course.course_id", primary_key=True)
  
