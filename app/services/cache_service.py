# app/services/cache_service.py
import asyncio
import functools
import json
from app.core.database import redis_pool


def cache(expire: int = 300):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # 生成缓存 key（可根据函数名 + 参数）
            key = f"cache:{func.__name__}:{hash(str(args) + str(kwargs))}"

            cached = await redis_pool.get(key)
            if cached:
                return json.loads(cached)

            result = await func(*args, **kwargs)
            await redis_pool.setex(key, expire, json.dumps(result))
            return result

        return wrapper

    return decorator