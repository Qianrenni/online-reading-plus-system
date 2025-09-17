import time
from fastapi import Request
from app.config.database import redis_client


async def log_request_middleware(request: Request, call_next):
    """
    请求日志中间件
    """
    start_time = time.time()
    
    # 处理请求
    response = await call_next(request)
    
    # 记录请求信息
    process_time = time.time() - start_time
    log_data = {
        "method": request.method,
        "url": str(request.url),
        "status_code": response.status_code,
        "process_time": f"{process_time:.4f}s",
        "client_host": request.client.host,
    }
    
    # 将日志信息存储到Redis
    await redis_client.lpush("request_logs", str(log_data))
    
    return response