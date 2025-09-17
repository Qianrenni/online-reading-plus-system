from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from motor.motor_asyncio import AsyncIOMotorClient
import redis.asyncio as redis
from .settings import settings


# MySQL异步引擎
engine = create_async_engine(
    settings.database_url,
    echo=True,
    future=True
)

# 创建异步session工厂
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


# MongoDB异步客户端
mongo_client = AsyncIOMotorClient(settings.mongodb_url)
mongodb = mongo_client.get_default_database()


# Redis异步客户端
redis_client = redis.from_url(settings.redis_url)


# 依赖项
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


async def get_mongo_db():
    return mongodb


async def get_redis():
    return redis_client
