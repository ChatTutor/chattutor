from typing import Optional
from sqlmodel import Field, Session, SQLModel, create_engine
import uuid as uuid_pkg
from datetime import datetime
from sqlalchemy import Field
from sqlmodel import Field

class Chat(SQLModel, table=True):
    """Chat Model
    
    chat_id (UUID): factory generated id

    Args:
        SQLModel (SQLModel): SQLModel
        table (bool, optional): Defaults to True.
    """
    chat_id: uuid_pkg.UUID = Field(
        default_factory=uuid_pkg.uuid4,
        primary_key=True,
        index=True,
        nullable=False,
    )
