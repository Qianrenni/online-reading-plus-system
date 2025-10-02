import enum

from pydantic import BaseModel


class ResponseCode(enum.IntEnum):
    SUCCESS = 0
    ERROR = 1


class ResponseModel(BaseModel):
    """
    响应模型
    """
    code: ResponseCode = ResponseCode.SUCCESS
    message: str = ""
    data: object = None
