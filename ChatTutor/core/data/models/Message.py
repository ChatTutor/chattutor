from typing import Optional
from sqlmodel import Field, Session, SQLModel, create_engine
import uuid as uuid_pkg
from datetime import datetime
from sqlalchemy import Field
from sqlmodel import Field

class Message(SQLModel, table=True):
    """### Message Model
    
    Columns:
        - role (str) : "assistant" | "user" - who sent the message
        - content (str) : message content
        - chat_key (UUID) : foreign_key "chat.chat_id" - id of the chat the 
                        message was sent in
        - clear_number (Optional[int]) : number of clears that happened until message
        - time_created (datetime) : defaults to factoy generated datetime.now
        - credential_token (str) : credential token of user [Not used yet] : TODO

    Args:
        SQLModel (SQLModel): SQLModel
        table (bool, optional): Defaults to True.
    """
    mes_id: uuid_pkg.UUID = Field(
        default_factory=uuid_pkg.uuid4,
        primary_key=True,
        index=True,
        nullable=False,
    )
    role: str
    content: str
    chat_key: uuid_pkg.UUID = Field(foreign_key="chat.chat_id")
    clear_number: Optional[int]
    time_created : datetime = Field(default_factory=datetime.now)
    credential_token : str
