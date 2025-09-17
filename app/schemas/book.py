from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class BookBase(BaseModel):
    title: str
    author: str
    description: Optional[str] = None


class BookCreate(BookBase):
    pass


class BookUpdate(BookBase):
    is_published: Optional[bool]


class BookInDBBase(BookBase):
    id: int
    is_published: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class Book(BookInDBBase):
    pass


class BookContentBase(BaseModel):
    book_id: int
    chapter_title: str
    content: str
    chapter_number: int


class BookContentCreate(BookContentBase):
    pass


class BookContentUpdate(BookContentBase):
    pass


class BookContentInDBBase(BookContentBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class BookContent(BookContentInDBBase):
    pass