from app.models.book import Book
from app.models.book_content import BookContent
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select


async def get_books(db: AsyncSession, skip: int = 0, limit: int = 100):
    """
    获取书籍列表
    """
    result = await db.execute(select(Book).offset(skip).limit(limit))
    return result.scalars().all()


async def get_book(db: AsyncSession, book_id: int):
    """
    根据ID获取书籍详情
    """
    result = await db.execute(select(Book).where(Book.id == book_id))
    return result.scalar_one_or_none()


async def get_book_contents(db: AsyncSession, book_id: int):
    """
    获取书籍章节内容
    """
    result = await db.execute(select(BookContent).where(BookContent.book_id == book_id))
    return result.scalars().all()


async def create_book(db: AsyncSession, book_data: dict):
    """
    创建新书籍
    """
    book = Book(**book_data)
    db.add(book)
    await db.commit()
    await db.refresh(book)
    return book