import datetime
from typing import Optional

from sqlmodel import SQLModel, Field


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True)
    password: str = Field(index=True)
    email: str = Field(index=True)
    is_active: bool = Field(default=True)
    avatar: str = Field(default="")
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)