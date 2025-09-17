from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.config.database import get_db

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/dashboard")
async def admin_dashboard(
    db: AsyncSession = Depends(get_db)
):
    # 管理员仪表盘
    pass


@router.post("/books")
async def create_book(
    db: AsyncSession = Depends(get_db)
):
    # 创建书籍
    pass


@router.put("/books/{book_id}")
async def update_book(
    book_id: int,
    db: AsyncSession = Depends(get_db)
):
    # 更新书籍
    pass