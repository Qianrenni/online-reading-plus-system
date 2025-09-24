# app/services/cache_service.py

import functools
import hashlib
import json
from typing import Any, Callable, List

from app.core.database import redis_pool
from app.middleware.logging import logger


def cache(
        expire: int = 300,
        ignore_null: bool = True,
        exclude_args: List[int] = None,
        exclude_kwargs: List[str] = None,
        key_prefix: str = None
    ):
    """
    缓存装饰器
    :param expire: 过期时间（秒）
    :param ignore_null: 是否忽略空值（None, {}, []）
    :param exclude_args: 排除的位置参数索引（如 [0] 表示排除第一个参数）
    :param exclude_kwargs: 排除的关键字参数名（如 ["database"]）
    """
    exclude_args = exclude_args or []
    exclude_kwargs = exclude_kwargs or []

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            try:
                # 过滤掉不需要参与缓存 key 生成的参数
                filtered_args = [
                    arg for i, arg in enumerate(args) if i not in exclude_args
                ]
                filtered_kwargs = {
                    k: v for k, v in kwargs.items() if k not in exclude_kwargs
                }

                # 序列化（确保顺序一致）
                serialized = json.dumps({
                    "args": filtered_args,
                    "kwargs": filtered_kwargs
                }, sort_keys=True, default=str)

                key_hash = hashlib.md5(serialized.encode()).hexdigest()
                if  key_prefix:
                    key = f"{key_prefix}:{key_hash}"
                else:
                    key = f"cache:{func.__module__}.{func.__name__}:{key_hash}"

            except Exception as e:
                logger.error(f"Cache key generation failed: {e}")
                return await func(*args, **kwargs)

            try:
                cached = await redis_pool.get(key)
                if cached is not None:
                    logger.info(f"Cache hit: {key}")
                    return json.loads(cached)
                else:
                    logger.info(f"Cache miss: {key}")
            except Exception as e:
                logger.error(f"Cache read failed: {e}")

            try:
                result = await func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Function execution failed: {e}")
                raise

            should_cache = True
            if ignore_null and (result is None or result == {} or result == []):
                should_cache = False

            if should_cache:
                try:
                    await redis_pool.setex(key, expire, json.dumps(result, default=str))
                    logger.info(f"Cache set: {key} (expire={expire}s)")
                except Exception as e:
                    logger.error(f"Cache write failed: {e}")

            return result

        return wrapper

    return decorator