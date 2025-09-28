# app/core/database.py
from redis import asyncio as aioredis
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import settings

# redis 配置
redis_pool = aioredis.from_url(settings.REDIS_URL)

# MySQL 异步引擎
engine = create_async_engine(
    url=settings.MYSQL_DSN,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False,
)


def get_shard_table_name(base_name: str, book_id: int) -> str:
    """
    :param base_name: 表名
    :param book_id:  书籍Id
    :return:  分表名
    """

    shard_id = book_id % settings.BOOK_SHARD_COUNT
    return f"{base_name}_shard_{shard_id}"


async def create_database_and_tables():
    """
    创建数据库和表
    """
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session():
    async with AsyncSession(engine) as session:
        yield session
