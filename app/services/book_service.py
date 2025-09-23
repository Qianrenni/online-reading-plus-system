from pandas.core.computation.expressions import where
from sqlmodel import select

from app.core.database import DataBaseSessionDepency
from app.models.sql import BookChapter
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

    @staticmethod
    async def get_book_by_id(
            book_id: int,
            database: DataBaseSessionDepency
    ) -> Book:
        """
        获取图书信息
        :param book_id: 图书ID
        :param database:    数据库会话
        :return:    图书信息
        """
        statement = select(Book).where(Book.id == book_id)
        result = await database.exec(statement)
        book = result.one()
        return book

    @staticmethod
    async def get_book_toc_by_id(
            book_id: int,
            database: DataBaseSessionDepency
    ) :
        """
        获取图书目录
        :param book_id: 图书ID
        :param database:      数据库会话
        :return:       图书目录
        """
        statement = select(BookChapter.id,BookChapter.title).where(BookChapter.book_id == book_id)
        result = await database.exec(statement)
        toc = result.all()
        return [[chapter[0],chapter[1]] for chapter in toc]

    @staticmethod
    async def get_book_chapter_by_id(
            chapter_id: int,
            database: DataBaseSessionDepency
    ) -> str:
        """
        获取图书章节内容
        :param book_id:      图书ID
        :param chapter_id:    章节ID
        :param database:         数据库会话
        :return:          章节内容
        """
        statement =select(BookChapter.content).where(BookChapter.id  == chapter_id)
        result = await database.exec(statement)
        chapter = result.one()
        return chapter

    @staticmethod
    async def get_book_chapter_by_index(
            book_id: int,
            chapter_index: int,
            database: DataBaseSessionDepency,
            ) -> str:
        """
        获取图书章节内容
        :param book_id:        图书ID
        :param chapter_index:     章节索引
        :param database:             数据库会话
        :return:             章节内容
        """
        statement = select(BookChapter.content).order_by(BookChapter.sort_order).limit(1).offset(chapter_index)
        result = await database.exec(statement)
        chapter = result.one()
        return chapter
book_service = BookService()