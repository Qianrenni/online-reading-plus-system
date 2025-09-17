from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ReadingHistoryBase(BaseModel):
    user_id: int
    book_id: int
    chapter_id: int
    progress: Optional[int] = 0


class ReadingHistoryCreate(ReadingHistoryBase):
    pass


class ReadingHistoryUpdate(ReadingHistoryBase):
    progress: Optional[int]


class ReadingHistoryInDBBase(ReadingHistoryBase):
    id: int
    last_read_at: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class ReadingHistory(ReadingHistoryInDBBase):
    pass