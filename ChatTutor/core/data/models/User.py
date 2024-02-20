from typing import Deque, List, Optional, Tuple
from sqlmodel import Field, Session, SQLModel, create_engine
import uuid as uuid_pkg
from datetime import datetime
from sqlmodel import Field, Relationship
from core.data.models.Course import Course
from core.data.models.SectionCourseLink import SectionCourseLink
from core.data.models.UserCourseLink import UserCourseLink
from dataclasses import dataclass

@dataclass
class User(SQLModel, table=True):
    """User Model
    
    Columns:
        - username (str): primary_key - username of user
        - email (str): email
        - password (str): hashed pwd of the user
        - user_type (str): type of the user
    
    Links:
        - courses (List[Course]): courses owned by this user [UserCourseLink]


    Args:
        SQLModel (SQLModel): SQLModel
        table (bool, optional): Defaults to True.
    """
    username : str = Field(primary_key=True)
    email : str
    password : str
    user_type : str
    courses: List[Course] = Relationship(back_populates="users", link_model=UserCourseLink)
    
    def jsonserialize(self):
        d = self.__dict__
        d["_sa_instance_state"] = None
        return d