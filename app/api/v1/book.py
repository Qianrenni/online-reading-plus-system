from fastapi import APIRouter, Path
from app.core.config import settings
from app.core.database import DataBaseSessionDepency
from app.models.sql import Book
from app.services.book_service import book_service
from app.services.cache_service import cache

book_router  = APIRouter(prefix="/book", tags=["book"])

@book_router.get("/category")
@cache(expire=settings.BOOK_CACHE_EXPIRE,exclude_kwargs=["database"])
async def get_book_category(database: DataBaseSessionDepency)-> list[str]:
    """
    获取图书分类
    :param database:    数据库会话
    :return:    分类列表
    """
    return await book_service.get_category(database=database)


@book_router.get("/{book_id}",response_model=Book)
@cache(expire=settings.BOOK_CACHE_EXPIRE,exclude_kwargs=["database"])
async def get_book(
        database: DataBaseSessionDepency
        ,book_id: int = Path(..., title="book_id", description="book_id", gt=0)):
    """
    获取图书信息
    :param database:     数据库会话
    :param book_id:       图书ID
    :return:      图书信息
    """
    return await  book_service.get_book_by_id(book_id=book_id, database=database)

@book_router.get("/toc/{book_id}")
@cache(expire=settings.BOOK_CACHE_EXPIRE,exclude_kwargs=["database"])
async def get_book_toc(
        database: DataBaseSessionDepency
        ,book_id: int = Path(..., title="book_id", description="book_id", gt=0)):
    """
    获取图书目录
    :param database:      数据库会话
    :param book_id:         图书ID
    :return:         图书目录
    """
    return await book_service.get_book_toc_by_id(book_id=book_id, database=database)

@book_router.get("/chapter/{book_id}/{chapter_id}")
@cache(expire=settings.BOOK_CACHE_EXPIRE,exclude_kwargs=["database"])
async def get_book_chapter(
        database: DataBaseSessionDepency
        ,book_id: int = Path(..., title="book_id", description="book_id", gt=0)
        ,chapter_id: int = Path(..., title="chapter_id", description="chapter_id", gt=0))-> str:
    """
    获取图书章节
    :param database:        数据库会话
    :param book_id:           图书ID
    :param chapter_id:         章节ID
    :return:           章节内容
    """
    return await book_service.get_book_chapter_by_id(book_id=book_id, chapter_id=chapter_id, database=database)
