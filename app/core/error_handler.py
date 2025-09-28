import functools
from typing import Callable

from starlette import status
from starlette.responses import JSONResponse

from app.middleware.logging import logger
from app.models.response_model import ResponseModel, ResponseCode


class CustomException(Exception):
    def __init__(
            self,
            status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
            message: str = None,
            headers: dict = None,
            media_type: str = "application/json",
            is_error: bool = False,
    ):
        """
        自定义异常类
        :param status_code: HTTP状态码
        :param message: 错误信息
        :param headers: HTTP头
        :param media_type: 响应媒体类型,
        :param is_error  : 错误类型
        """
        super().__init__(self.message)
        self.status_code = status_code
        self.message = message
        self.headers = headers
        self.media_type = media_type
        self.isError = is_error


def wrap_error_handler_api(
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        message: str = None,
        headers: dict = None,
        media_type: str = "application/json",
        # background: list = None

):
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except CustomException as e:
                logger.error(
                    f"{func.__qualname__} "
                    f"args {' '.join([str(arg) for arg in args if isinstance(arg, (str, int))])} "
                    f"kwargs {' '.join([f'{k} {v}' for k, v in kwargs.items() if isinstance(v, (str, int))])} "
                    f"{str(e)}"
                )
                return JSONResponse(
                    status_code=e.status_code,
                    content=ResponseModel(
                        code=ResponseCode.ERROR,
                        message=str(e) if e.message is None else e.message
                    ).json(),
                    headers=e.headers,
                    media_type=e.media_type
                )
            except Exception as e:
                logger.error(
                    f"{func.__qualname__} "
                    f"args {' '.join([str(arg) for arg in args if isinstance(arg, (str, int))])} "
                    f"kwargs {' '.join([f'{k} {v}' for k, v in kwargs.items() if isinstance(v, (str, int))])} "
                    f"{str(e)}"
                )
                return JSONResponse(
                    status_code=status_code,
                    content=ResponseModel(
                        code=ResponseCode.ERROR,
                        message=str(e) if message is None else message
                    ).json(),
                    headers=headers,
                    media_type=media_type
                )

        return wrapper

    return decorator
