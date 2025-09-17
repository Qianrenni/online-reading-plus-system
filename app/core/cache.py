import functools
import pickle
from typing import Any, Callable
from app.config.database import redis_client


async def get_cache(key: str) -> Any:
    """
    从Redis缓存中获取数据
    """
    value = await redis_client.get(key)
    if value:
        return pickle.loads(value)
    return None


async def set_cache(key: str, value: Any, expire: int = 3600):
    """
    将数据存储到Redis缓存中
    """
    await redis_client.set(key, pickle.dumps(value), ex=expire)


async def delete_cache(key: str):
    """
    从Redis缓存中删除数据
    """
    await redis_client.delete(key)


def cached(expire: int = 3600):
    """
    缓存装饰器
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # 尝试从缓存获取
            cached_result = await get_cache(cache_key)
            if cached_result is not None:
                return cached_result
            
            # 执行函数并缓存结果
            result = await func(*args, **kwargs)
            await set_cache(cache_key, result, expire)
            return result
        return wrapper
    return decorator