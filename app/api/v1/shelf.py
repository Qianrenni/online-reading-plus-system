from typing import Annotated

from fastapi import APIRouter, Depends, Body,status
from app.core.database import DataBaseSessionDepency
from app.core.security import get_current_user
from app.models.response_model import ResponseModel
from app.services.shelf_service import shelf_service

shelf_router =  APIRouter(prefix='/shelf', tags=["shelf"],dependencies=[Depends(get_current_user)])
@shelf_router.get('/get', response_model=ResponseModel)
async def get_shelf(database: DataBaseSessionDepency,current_user = Depends(get_current_user)):
    """
    获取用户书架
    :param current_user:    当前用户
    :param user_id: 用户ID
    :param database:    数据库会话
    :return:    书架列表
    """
    result  = await shelf_service.get_shelf(user_id=current_user['id'], database=database)
    return  ResponseModel(data = result)

@shelf_router.post('/add',response_model=ResponseModel, status_code=status.HTTP_201_CREATED)
async def add_shelf(book_id: Annotated[int,Body(embed=True)], database: DataBaseSessionDepency,current_user = Depends(get_current_user)):
    """
    添加图书到书架
    :param book_id:  图书ID
    :param database:    数据库会话
    :param current_user:    当前用户
    :return:       添加结果
    """
    try:
        result = await shelf_service.add_shelf(book_id=book_id, user_id=current_user['id'], database=database)
        if  result:
            return    ResponseModel()
        else:
            return ResponseModel(code=-1,message="添加失败")
    except Exception as e:
        return ResponseModel(code=-1,message=f"添加失败{str(e)}")




