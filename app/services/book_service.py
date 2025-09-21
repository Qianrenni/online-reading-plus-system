from sqlmodel import select

from app.core.database import DataBaseSessionDepency
from app.models.sql.Book import Book


class BookService:

    @staticmethod
    async def get_category(
            database: DataBaseSessionDepency
    ) -> list[str]:
        """
        获取图书分类
        return: 分类列表
        """
        statement = select(Book.category).distinct()
        result = await database.exec(statement)
        categories = result.all()
        return [category for category in categories]


book_service = BookService()