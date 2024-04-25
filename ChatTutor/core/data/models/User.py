from typing import Deque, List, Optional, Tuple
from sqlmodel import Field, Session, SQLModel, create_engine
import uuid as uuid_pkg
from datetime import datetime
from sqlmodel import Field, Relationship

# from core.data.models.Course import Course
from core.data.models.StudentCourseLink import StudentCourseLink
from core.data.models.SectionCourseLink import SectionCourseLink
from core.data.models.UserCourseLink import UserCourseLink
from dataclasses import dataclass
import flask_login
import bcrypt


@dataclass
class User(flask_login.UserMixin, SQLModel, table=True):
    """User Model

    Columns:
        - username (str): primary_key - username of user
        - email (str): email
        - password_hash (str): hashed pwd of the user
        - user_type (str): type of the user

    Links:
        - courses (List[Course]): courses owned by this user [UserCourseLink]


    Args:
        SQLModel (SQLModel): SQLModel
        table (bool, optional): Defaults to True.
    """

    user_id: str = Field(
        default_factory=uuid_pkg.uuid4,
        primary_key=True,
        index=True,
        nullable=False,
    )
    google_id: Optional[str]
    name: Optional[str]
    email: str
    password_hash: str
    user_type: str
    courses: List["Course"] = Relationship(back_populates="users", link_model=UserCourseLink)
    studied_courses: List["Course"] = Relationship(
        back_populates="students", link_model=StudentCourseLink
    )
    verified: str = Field(default="false")

    def get_id(self):
        return self.email

    def jsonserialize(self):
        d = self.__dict__
        d["_sa_instance_state"] = None
        return d

    @property
    def password(self):
        raise AttributeError("password not readable")

    @password.setter
    def password(self, password):
        self.password_hash = bcrypt.hashpw(password.encode("utf-8", "ignore"), bcrypt.gensalt())

    def set_password(self, password):
        self.password_hash = bcrypt.hashpw(password.encode("utf-8", "ignore"), bcrypt.gensalt())

    def verify_password(self, p):
        print(
            self.password_hash,
            bcrypt.hashpw(p.encode("utf8", "ignore"), bcrypt.gensalt()).decode("utf-8"),
        )
        print(
            self.password_hash,
            bcrypt.hashpw(p.encode("utf8", "ignore"), bcrypt.gensalt()).decode("utf-8"),
        )
        print(self.password_hash.encode("utf-8"), p.encode("utf-8"))
        return bcrypt.checkpw(p.encode("utf-8"), self.password_hash.encode("utf-8"))
