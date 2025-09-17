from app.models.reading_history import ReadingHistory
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select


async def get_reading_history(db: AsyncSession, user_id: int):
    """
    获取用户阅读历史
    """
    result = await db.execute(select(ReadingHistory).where(ReadingHistory.user_id == user_id))
    return result.scalars().all()


async def record_reading_progress(db: AsyncSession, reading_data: dict):
    """
    记录阅读进度
    """
    # 检查是否已存在阅读记录
    result = await db.execute(
        select(ReadingHistory).where(
            ReadingHistory.user_id == reading_data['user_id'],
            ReadingHistory.book_id == reading_data['book_id'],
            ReadingHistory.chapter_id == reading_data['chapter_id']
        )
    )
    reading_record = result.scalar_one_or_none()
    
    if reading_record:
        # 更新现有记录
        for key, value in reading_data.items():
            setattr(reading_record, key, value)
    else:
        # 创建新记录
        reading_record = ReadingHistory(**reading_data)
        db.add(reading_record)
    
    await db.commit()
    await db.refresh(reading_record)
    return reading_record