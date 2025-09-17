from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.schemas.reading import ReadingHistory
from app.config.database import get_db

router = APIRouter(prefix="/reading", tags=["reading"])


@router.get("/history", response_model=List[ReadingHistory])
async def read_reading_history(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    # 获取用户阅读历史
    pass


@router.post("/history")
async def record_reading_progress(
    reading_history: ReadingHistory,
    db: AsyncSession = Depends(get_db)
):
    # 记录阅读进度
    pass