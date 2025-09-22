from pydantic import BaseModel


class ResponseModel(BaseModel):
    """
    响应模型
    """
    code: int = 0
    msg: str =  ""
    data: object = None