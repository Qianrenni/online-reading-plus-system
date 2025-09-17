from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.config.database import get_db

router = APIRouter(prefix="/ads", tags=["advertisements"])


@router.get("/", response_model=List[dict])
async def get_active_ads(
    db: AsyncSession = Depends(get_db)
):
    # 获取活跃广告列表
    pass


@router.post("/click/{ad_id}")
async def record_ad_click(
    ad_id: int,
    db: AsyncSession = Depends(get_db)
):
    # 记录广告点击
    pass