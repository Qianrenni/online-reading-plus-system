from fastapi import APIRouter, Path
from sqlalchemy.sql.annotation import Annotated

from app.core.database import DataBaseSessionDepency
from app.services.book_service import book_service
from app.services.cache_service import cache

book_router  = APIRouter(prefix="/book", tags=["book"])

@book_router.get("/category")
@cache(expire=7*24*60*60,exclude_kwargs=["database"])
async def get_book_category(database: DataBaseSessionDepency):
    return await book_service.get_category(database=database)


@book_router.get("/{book_id}")
async def get_book(book_id: int = Path(..., title="book_id", description="book_id", gt=0)):
    return {"book_id": book_id}
