from typing import Optional
from sqlmodel import Field, Session, SQLModel, create_engine
import uuid as uuid_pkg
from datetime import datetime
from sqlalchemy import Field
from sqlmodel import Field

class UserCourseLink(SQLModel, table=True):
    """User <-> Course Link (MtoM)
    
    Columns:
        - username (str): foreign_key "user.username" - username of user
        - course_id (UUID): foreign_key "course.course_id" - id of section

    Args:
        SQLModel (SQLModel): SQLModel
        table (bool, optional): Defaults to True.
    """
    username: str = Field(foreign_key="user.username", primary_key=True)
    course_id: uuid_pkg.UUID = Field(foreign_key="course.course_id", primary_key=True)
