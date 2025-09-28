from fastapi import APIRouter, Path
from fastapi.params import Depends, Query
from typing import Annotated

from pydantic import Field
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core import wrap_error_handler_api
from app.core.config import settings
from app.core.database import get_session
from app.core.security import get_current_user
from app.models.response_model import ResponseModel
from app.services.book_service import book_service
from app.services.cache_service import cache

book_router = APIRouter(prefix="/book", tags=["book"])


@book_router.get("/total", response_model=ResponseModel)
@cache(expire=settings.BOOK_CACHE_EXPIRE, exclude_kwargs=["database"])
@wrap_error_handler_api()
async def get_books_total_count(
        database: Annotated[AsyncSession, Depends(get_session)],
):
    """
    获取图书总数
    :param database:         数据库会话
    :return:                   图书总数
    """
    result = await book_service.get_books_total_count(database=database)
    return ResponseModel(data={"total": result})


@book_router.get("/category", response_model=ResponseModel)
@cache(expire=settings.BOOK_CACHE_EXPIRE, exclude_kwargs=["database"])
@wrap_error_handler_api()
async def get_book_category(
        database: Annotated[AsyncSession, Depends(get_session)]
):
    """
    获取图书分类
    :param database:    数据库会话
    :return:    分类列表
    """
    result = await book_service.get_category(database=database)
    return ResponseModel(data=result)


@book_router.get("/list", response_model=ResponseModel)
@wrap_error_handler_api()
async def get_book_list(
        book_ids: Annotated[
            list[Annotated[int, Field(gt=0)]],
            Query(
                title="book_ids",
                description="List of book IDs to fetch",
            )],
        database: Annotated[AsyncSession, Depends(get_session)]

):
    """
    获取图书信息
    :param book_ids:      图书ID列表
    :return:             图书信息列表
    """
    result = await book_service.get_book_by_list(book_ids=book_ids, database=database)
    return ResponseModel(data=result)


@book_router.get("/{book_id}", response_model=ResponseModel)
@wrap_error_handler_api()
async def get_book(
        database: Annotated[AsyncSession, Depends(get_session)]
        , book_id: int = Path(..., title="book_id", description="book_id", gt=0)):
    """
    获取图书信息
    :param database:     数据库会话
    :param book_id:       图书ID
    :return:      图书信息
    """
    result = await  book_service.get_book_by_id(book_id=book_id, database=database)
    return ResponseModel(data=result)


@book_router.get("/toc/{book_id}", response_model=ResponseModel)
@cache(expire=settings.BOOK_CACHE_EXPIRE, exclude_kwargs=["database"])
@wrap_error_handler_api()
async def get_book_toc(
        database: Annotated[AsyncSession, Depends(get_session)]
        , book_id: int = Path(..., title="book_id", description="book_id", gt=0)):
    """
    获取图书目录
    :param database:      数据库会话
    :param book_id:         图书ID
    :return:         图书目录
    """
    result = await book_service.get_book_toc_by_id(book_id=book_id, database=database)
    return ResponseModel(data=result)


@book_router.get("/chapter/{id}", dependencies=[Depends(get_current_user)], response_model=ResponseModel)
@cache(expire=settings.BOOK_CACHE_EXPIRE, exclude_kwargs=["database"])
@wrap_error_handler_api()
async def get_book_chapter(
        database: Annotated[AsyncSession, Depends(get_session)]
        , id: int = Path(..., title="id", description="id", gt=0)):
    """
    获取图书章节
    :param database:        数据库会话
    :param id:         ID
    :return:           章节内容
    """
    result = await book_service.get_book_chapter_by_id(chapter_id=id, database=database)
    return ResponseModel(data=result)


@book_router.get("/chapter/{book_id}/{chapter_index}", dependencies=[Depends(get_current_user)],
                 response_model=ResponseModel)
@cache(expire=settings.BOOK_CACHE_EXPIRE, exclude_kwargs=["database"])
@wrap_error_handler_api()
async def get_book_chapter_by_index(
        database: Annotated[AsyncSession, Depends(get_session)],
        book_id: int = Path(..., title="book_id", description="book_id", gt=0),
        chapter_index: int = Path(..., title="chapter_index", description="chapter_index", gt=-1)):
    """
    获取图书章节
    :param database:         数据库会话
    :param book_id:              图书ID
    :param chapter_index:         章节索引
    :return:                  章节内容
    """
    result = await book_service.get_book_chapter_by_index(book_id=book_id, chapter_index=chapter_index,
                                                          database=database)
    return ResponseModel(data=result)
