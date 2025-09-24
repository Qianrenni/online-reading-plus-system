from pydantic import BaseModel


class ResponseModel(BaseModel):
    """
    响应模型
    """
    code: int = 0
    message: str = ""
    data: object = None