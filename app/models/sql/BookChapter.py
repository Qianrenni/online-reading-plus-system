from datetime import datetime
from typing import Optional

from sqlalchemy import Index, Column, Text
from sqlalchemy.dialects.mysql import MEDIUMTEXT
from sqlmodel import SQLModel, Field
from sympy.physics.optics import Medium


class BookChapter(SQLModel, table=True):
    __tablename__ =  "book_chapter"
    id: Optional[int] = Field(default=None, primary_key=True)
    book_id: int = Field(foreign_key="book.id", index=True)
    title: str = Field(default="")
    sort_order: float = Field(default=0.0, index=True)
    content: str = Field(
        default="",
        sa_column=Column(MEDIUMTEXT)
    )
    created_at: datetime = Field(default_factory=datetime.now)

    # 添加联合唯一索引（防止同一本书章节排序重复）
    __table_args__ = (
        Index("index_book_sort_unique", "book_id", "sort_order", unique=True),
    )