import asyncio

from sqlalchemy.exc import NoResultFound
from sqlalchemy.sql.functions import count
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import settings
from app.models.sql import BookChapter
from app.models.sql.Book import Book
from app.services.cache_service import cache, cache_get, cache_set


class BookService:

    @staticmethod
    async def get_category(
            database: AsyncSession
    ) -> list[str]:
        """
        获取图书分类
        return: 分类列表
        """
        statement = select(Book.category).distinct()
        result = await database.exec(statement)
        categories = result.all()
        return [str(category) for category in categories]

    @staticmethod
    @cache(expire=settings.BOOK_CACHE_EXPIRE,exclude_kwargs=["database"],key_prefix="get_book_by_id")
    async def get_book_by_id(
            book_id: int,
            database: AsyncSession
    ) -> Book|None:
        """
        获取图书信息
        :param book_id: 图书ID
        :param database:    数据库会话
        :return:    图书信息
        """
        try:
            statement = select(Book).where(Book.id == book_id)
            result = await database.exec(statement)
            book = result.one()
            book.cover =  f"{settings.SERVER_URL}/static/book/{book.id}/{book.cover}"
            return book
        except NoResultFound:
            return None  # 返回 None

    @staticmethod
    async def get_book_by_list(
        book_ids: list[int],
        database: AsyncSession
    ) -> list[Book]:
        """
        获取图书信息
        :param book_ids:  图书ID列表
        :param database:        数据库会话
        :return:         图书信息
        """
        if not book_ids:
            return []
        miss_book_ids = []
        book_list = []
        for book_id in book_ids:
            try:
                result = await cache_get(
                    args=[],
                    kwargs={"book_id": book_id},
                    key_prefix="get_book_by_id"
                )
                if result:
                    book_list.append(result)
                else:
                    miss_book_ids.append(book_id)
            except Exception as e:
                raise ValueError(f"获取图书信息失败{str(e)}")
        if miss_book_ids:
            statement = select(Book).where(Book.id.in_(miss_book_ids))
            result = await database.exec(statement)
            tasks =  [cache_set(
                                args=[],
                                kwargs={"book_id": book.id},
                                key_prefix="get_book_by_id",
                                value=book
                        )  for book in result.all()]
            await asyncio.gather(*tasks)
            book_list.extend(result.all())
        return  book_list

    @staticmethod
    async def get_book_toc_by_id(
            book_id: int,
            database: AsyncSession
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
            database: AsyncSession
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
        return str(chapter)

    @staticmethod
    async def get_book_chapter_by_index(
            book_id: int,
            chapter_index: int,
            database: AsyncSession,
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
        return str(chapter)

    @staticmethod
    async def get_books_total_count(
            database: AsyncSession,
    )->int:
        """
        获取图书总数
        :param database:      数据库会话
        :return:              图书总数
        """
        statement = select(count(Book.id))
        result =  await database.exec(statement)
        return result.one()
book_service = BookService()