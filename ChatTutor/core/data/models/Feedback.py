from typing import Optional
from sqlmodel import Field, Session, SQLModel, create_engine
import uuid as uuid_pkg
from datetime import datetime
from sqlalchemy import Field
from sqlmodel import Field

class Feedback(SQLModel, table=True):
    """### Feedback Model
    
    Columns:
        - feedback_id (UUID) : factory generated feedback id
        - message_id (UUID) : foreign_key "message.message_id"
        - content (str) : content
    Args:
        SQLModel (SQLModel): SQLModel
        table (bool, optional): Defaults to True.
    """
    feedback_id: uuid_pkg.UUID = Field(
        default_factory=uuid_pkg.uuid4,
        primary_key=True,
        index=True,
        nullable=False,
    )
    message_id: uuid_pkg.UUID = Field(foreign_key="message.message_id")
    content: str
