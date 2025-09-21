from datetime import datetime
from typing import Optional

from sqlalchemy import Index
from sqlmodel import SQLModel, Field


class Shelf(SQLModel,table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    book_id: int = Field(foreign_key="book.id", index=True)
    created_at: datetime = Field(default_factory=datetime.now)
    last_read_at: datetime = Field(default_factory=datetime.now)
    # 联合唯一索引：一个用户不能重复添加同一本书到书架
    __table_args__ = (
        Index("index_user_book_unique", "user_id", "book_id", unique=True),
        Index("index_user_last_read", "user_id", "last_read_at"),
    )
