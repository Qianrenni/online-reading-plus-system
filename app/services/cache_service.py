# app/services/cache_service.py

import asyncio
import functools
import hashlib
import json
import uuid
from typing import Callable,Any

from app.core.database import redis_pool
from app.middleware.logging import logger


def generate_cache_key(
    args: list[Any]|None=None,
    kwargs: dict[str, Any]|None=None,
    exclude_args: list[int] | None= None,
    exclude_kwargs: list[str] | None= None,
    key_prefix: str | None= None,
) -> str:
    """
    统一生成缓存 key 的函数
    """
    args = args or []
    kwargs = kwargs or {}
    exclude_args = exclude_args or []
    exclude_kwargs = exclude_kwargs or []

    filtered_args = [arg for i, arg in enumerate(args) if i not in exclude_args]
    filtered_kwargs = {k: v for k, v in kwargs.items() if k not in exclude_kwargs}

    serialized = json.dumps(
        {"args": filtered_args, "kwargs": filtered_kwargs},
        sort_keys=True,
        default=str,
    )

    key_hash = hashlib.md5(serialized.encode()).hexdigest()
    return f"{key_prefix}:{key_hash}"


async def _renew_lock(lock_key: str, lock_value: str, lock_timeout: int, interval: float | None= None):
    """
    后台任务：定期续期分布式锁
    """
    interval = interval or max(1, lock_timeout // 3)  # 至少1秒，避免过于频繁
    while True:
        try:
            # 使用 Lua 脚本安全续期：仅当锁仍属于当前持有者时才延长
            lua_script = """
            if redis.call("get", KEYS[1]) == ARGV[1] then
                return redis.call("expire", KEYS[1], ARGV[2])
            else
                return 0
            end
            """
            await redis_pool.eval(lua_script, 1, lock_key, lock_value, str(lock_timeout))
            logger.debug(f"Lock renewed: {lock_key}")
        except Exception as e:
            logger.warning(f"Failed to renew lock {lock_key}: {e}")
            break
        await asyncio.sleep(interval)


async def cache_get(
    *,
    args: list[Any]|None=None,
    kwargs: dict[str, Any]|None=None,
    expire: int = 300,
    ignore_null: bool = True,
    exclude_args: list[int] | None= None,
    exclude_kwargs: list[str] | None= None,
    key_prefix: str | None= None,
    lock_timeout: int = 10,
    fallback_func: Callable[..., Any] | None = None,
    fallback_args: tuple[Any, ...] = (),
    fallback_kwargs: dict[str, Any] | None= None,
) -> Any:
    """
    手动获取缓存，支持回源（带分布式锁 + 自动续期）

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
            logger.info(f"Cache hit: {cache_key}")
            return json.loads(cached)
    except Exception as e:
        logger.error(f"Cache read failed: {e}")

    # 2. 如果没有 fallback_func，直接返回 None
    if fallback_func is None:
        return None

    # 3. 有 fallback_func：尝试加锁回源
    lock_acquired = False
    lock_value = str(uuid.uuid4())
    renew_task = None

    try:
        # 尝试获取锁（带唯一值）
        lock_acquired = await redis_pool.set(lock_key, lock_value, ex=lock_timeout, nx=True)

        if lock_acquired:
            # 启动锁续期任务
            renew_task = asyncio.create_task(
                _renew_lock(lock_key, lock_value, lock_timeout)
            )

            # 双重检查：可能在加锁前已被写入
            cached = await redis_pool.get(cache_key)
            if cached is not None:
                return json.loads(cached)

            # 执行回源逻辑
            result = await fallback_func(*fallback_args, **fallback_kwargs)

            # 决定是否缓存
            should_cache = not (
                ignore_null and (result is None or result == {} or result == [])
            )
            if should_cache:
                await redis_pool.setex(
                    cache_key, expire, json.dumps(result)
                )
                logger.info(f"Cache set: {cache_key} (expire={expire}s)")

            return result
        else:
            # 未获取到锁：循环等待缓存被写入
            start_time = asyncio.get_event_loop().time()
            max_wait = lock_timeout + 1  # 略大于锁超时，防误判

            while asyncio.get_event_loop().time() - start_time < max_wait:
                await asyncio.sleep(0.05)
                cached = await redis_pool.get(cache_key)
                if cached is not None:
                    logger.info(f"Cache filled by another worker: {cache_key}")
                    return json.loads(cached)

            # 超时仍未命中，认为锁持有者失败，自己回源
            logger.warning(
                f"Cache still empty after {max_wait}s, "
                f"executing fallback directly: {cache_key}"
            )
            return await fallback_func(*fallback_args, **fallback_kwargs)

    except Exception as e:
        logger.error(f"Error in cache_get fallback: {e}")
        raise

    finally:
        # 停止锁续期任务
        if renew_task and not renew_task.done():
            renew_task.cancel()
            try:
                await renew_task
            except asyncio.CancelledError:
                pass
            except Exception as e:
                logger.warning(f"Error while cancelling lock renewal: {e}")

        # 安全释放锁（仅删除属于自己的锁）
        if lock_acquired:
            try:
                lua_script = """
                if redis.call("get", KEYS[1]) == ARGV[1] then
                    return redis.call("del", KEYS[1])
                else
                    return 0
                end
                """
                await redis_pool.eval(lua_script, 1, lock_key, lock_value)
            except Exception as e:
                logger.warning(f"Failed to release lock {lock_key}: {e}")


async def cache_set(
    *,
    value: Any,
    args: list[Any]|None=None,
    kwargs: dict[str, Any]|None=None,
    expire: int = 300,
    ignore_null: bool = True,
    exclude_args: list[int] | None = None,
    exclude_kwargs: list[str] | None = None,
    key_prefix: str | None  = None,
) -> bool:
    """
    手动设置缓存
    """
    if key_prefix is None or key_prefix == "":
        raise ValueError("key_prefix must be set")
    if ignore_null and (value is None or value == {} or value == []):
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
    *,
    args: list[Any]|None=None,
    kwargs: dict[str, Any]|None=None,
    exclude_args: list[int] | None = None,
    exclude_kwargs: list[str] | None = None,
    key_prefix: str | None= None,
) -> bool:
    """
    手动删除缓存项
    """
    if key_prefix is None or key_prefix == "":
        raise ValueError("key_prefix must be set")

    try:
        cache_key = generate_cache_key(
            args, kwargs, exclude_args, exclude_kwargs, key_prefix
        )
        result = await redis_pool.delete(cache_key)
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
    exclude_args: list[int] | None= None,
    exclude_kwargs: list[str] | None = None,
    key_prefix: str | None= None,
    lock_timeout: int = 10,
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
                key_prefix=key_prefix if key_prefix else func.__qualname__,
                lock_timeout=lock_timeout,
                fallback_func=_fallback,
                fallback_args=(),
                fallback_kwargs={},
            )

        return wrapper

    return decorator