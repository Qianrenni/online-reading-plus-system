from datetime import datetime

from sqlalchemy import Column, Text
from sqlmodel import SQLModel, Field


class Book(SQLModel ,table=True):
    id: int = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    author: str = Field(index=True)
    cover: str = Field(default="")
    description: str = Field(
        default="",
        sa_column=Column(Text)
    )
    category: str = Field(default="")
    tags: str = Field(default="")
    total_chapter: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.now)


