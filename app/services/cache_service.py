# app/services/cache_service.py

import asyncio
import functools
import hashlib
import json
from typing import Any, Callable, List, Optional, Union, Dict, Tuple

from app.core.database import redis_pool
from app.middleware.logging import logger


def generate_cache_key(
        args: List[Any],
        kwargs: Dict[str, Any],
        exclude_args: List[int] = None,
        exclude_kwargs: List[str] = None,
        key_prefix: str = None,
) -> str:
    """
    统一生成缓存 key 的函数
    """
    exclude_args = exclude_args or []
    exclude_kwargs = exclude_kwargs or []

    filtered_args = [arg for i, arg in enumerate(args) if i not in exclude_args]
    filtered_kwargs = {k: v for k, v in kwargs.items() if k not in exclude_kwargs}

    serialized = json.dumps({
        "args": filtered_args,
        "kwargs": filtered_kwargs
    }, sort_keys=True, default=str)

    key_hash = hashlib.md5(serialized.encode()).hexdigest()
    return f"{key_prefix}:{key_hash}"


async def cache_get(
        args: List[Any],
        kwargs: Dict[str, Any],
        *,
        expire: int = 300,
        ignore_null: bool = True,
        exclude_args: List[int] = None,
        exclude_kwargs: List[str] = None,
        key_prefix: str = None,
        lock_timeout: int = 10,
        fallback_func: Optional[Callable] = None,  # 回源函数：async def fallback() -> Any
        fallback_args: Tuple = (),
        fallback_kwargs: Dict = None
) -> Any:
    """
    手动获取缓存，支持回源（带分布式锁）

    :param args: 用于生成 key 的位置参数
    :param kwargs: 用于生成 key 的关键字参数
    :param fallback_func: 当缓存未命中时调用的异步函数
    :param fallback_args, fallback_kwargs: 传递给 fallback_func 的参数
    :return: 缓存值 或 fallback_func 的返回值
    """
    fallback_kwargs = fallback_kwargs or {}
    cache_key = generate_cache_key(
        args, kwargs, exclude_args, exclude_kwargs, key_prefix
    )
    lock_key = f"lock:{cache_key}"

    # 1. 尝试读缓存
    try:
        cached = await redis_pool.get(cache_key)
        if cached is not None:
            logger.info(f"Cache hit : {cache_key}")
            return json.loads(cached)
    except Exception as e:
        logger.error(f"Cache read failed : {e}")

    # 2. 如果没有 fallback_func，直接返回 None
    if fallback_func is None:
        return None

    # 3. 有 fallback_func：尝试加锁回源
    lock_acquired = False
    try:
        lock_acquired = await redis_pool.set(lock_key, "1", ex=lock_timeout, nx=True)

        if lock_acquired:
            # 双重检查：可能在加锁前已被写入
            cached = await redis_pool.get(cache_key)
            if cached is not None:
                return json.loads(cached)

            # 执行回源
            result = await fallback_func(*fallback_args, **fallback_kwargs)

            # 决定是否缓存
            should_cache = not (ignore_null and (result is None or result == {} or result == []))
            if should_cache:
                await redis_pool.setex(cache_key, expire, json.dumps(result, default=str))
                logger.info(f"Cache set : {cache_key} (expire={expire}s)")

            return result
        else:
            # 未获取到锁：等待后重试读缓存
            await asyncio.sleep(0.05)
            cached = await redis_pool.get(cache_key)
            if cached is not None:
                return json.loads(cached)
            else:
                # 极端情况：自己执行 fallback（可选，或抛异常）
                logger.warning(f"Lock holder may have failed, executing fallback directly: {cache_key}")
                return await fallback_func(*fallback_args, **fallback_kwargs)

    except Exception as e:
        logger.error(f"Error in cache_get fallback: {e}")
        raise
    finally:
        if lock_acquired:
            try:
                await redis_pool.delete(lock_key)
            except Exception as e:
                logger.warning(f"Failed to release lock {lock_key}: {e}")


async def cache_set(
        args: List[Any],
        kwargs: Dict[str, Any],
        value: Any,
        *,
        expire: int = 300,
        ignore_null: bool = True,
        exclude_args: List[int] = None,
        exclude_kwargs: List[str] = None,
        key_prefix: str =  None
) -> bool:
    """
    手动设置缓存
    """
    if key_prefix is None or  key_prefix == "":
        raise ValueError("key_prefix must be set")
    if  ignore_null and (value is None or value == {} or value == []):
        return False

    cache_key = generate_cache_key(
        args, kwargs, exclude_args, exclude_kwargs, key_prefix
    )

    try:
        await redis_pool.setex(cache_key, expire, json.dumps(value, default=str))
        logger.info(f"Manual cache set: {cache_key} (expire={expire}s)")
        return True
    except Exception as e:
        logger.error(f"Manual cache set failed: {e}")
        return False


async def cache_delete(
        args: List[Any],
        kwargs: Dict[str, Any],
        *,
        exclude_args: List[int] = None,
        exclude_kwargs: List[str] = None,
        key_prefix: str = None
) -> bool:
    """
    手动删除缓存项

    :param args: 用于生成 key 的位置参数
    :param kwargs: 用于生成 key 的关键字参数
    :param exclude_args: 排除的位置参数索引
    :param exclude_kwargs: 排除的关键字参数名
    :param key_prefix: key 前缀（必须与写入时一致）
    :return: 是否删除成功（Redis 删除不存在的 key 也会返回 1，所以这里只看是否抛异常）
    """
    if key_prefix is None or key_prefix == "":
        raise ValueError("key_prefix must be set")

    try:
        cache_key = generate_cache_key(
            args, kwargs, exclude_args, exclude_kwargs, key_prefix
        )
        result = await redis_pool.delete(cache_key)
        # Redis delete 返回被删除的 key 数量（0 或 1）
        deleted = result > 0
        if deleted:
            logger.info(f"Cache deleted: {cache_key}")
        else:
            logger.info(f"Cache key not found for deletion: {cache_key}")
        return deleted
    except Exception as e:
        logger.error(f"Cache delete failed: {e}")
        return False

def cache(
        expire: int = 300,
        ignore_null: bool = True,
        exclude_args: List[int] = None,
        exclude_kwargs: List[str] = None,
        key_prefix: str = None,
        lock_timeout: int = 10
):
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            async def _fallback():
                return await func(*args, **kwargs)

            return await cache_get(
                args=list(args),
                kwargs=kwargs,
                expire=expire,
                ignore_null=ignore_null,
                exclude_args=exclude_args,
                exclude_kwargs=exclude_kwargs,
                key_prefix=key_prefix if  key_prefix else func.__qualname__,
                lock_timeout=lock_timeout,
                fallback_func=_fallback,
                fallback_args=(),
                fallback_kwargs={}
            )

        return wrapper
    return decorator