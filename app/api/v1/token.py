import json
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core import wrap_error_handler_api
from app.core.database import get_session
from app.core.security import create_access_token, get_current_user
from app.models.response_model import ResponseModel
from app.models.sql.User import User
from app.services.user_service import UserService

token_router = APIRouter(prefix='/token', tags=["token"])


class Token(ResponseModel):
    """
    令牌模型
    - data
    - - access_token (str): 访问令牌
    - - token_type (str): 令牌类型
    """
    data: dict[str, str] = {"access_token": "", "token_type": "Bearer"}


@token_router.post('/get', response_model=Token)
@wrap_error_handler_api(status_code=status.HTTP_401_UNAUTHORIZED, headers={"WWW-Authenticate": "Bearer"})
async def login_for_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        database: Annotated[AsyncSession, Depends(get_session)]
) -> ResponseModel:
    """
    处理用户登录请求并生成访问令牌
    
    该函数接收用户名和密码，验证用户身份后生成JWT访问令牌。
    如果认证失败，将抛出HTTP 401未授权异常。
    
    - param form_data: OAuth2密码请求表单数据，包含用户名(邮箱)和密码
    - return: 包含访问令牌和令牌类型的Token对象
    - raises HTTPException: 当用户名或密码不正确时抛出401未授权异常
    """
    user_dict = {"user_email": form_data.username, "password": form_data.password}
    user = await UserService.authenticate_user(db=database, **user_dict)
    access_token = create_access_token(
        data={"sub": json.dumps({
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "avatar": user.avatar,
            "is_active": user.is_active,
        })}
    )
    return Token(data={"access_token": access_token, "token_type": "Bearer"})


@token_router.post('/refresh', response_model=Token)
@wrap_error_handler_api(status_code=status.HTTP_401_UNAUTHORIZED, headers={"WWW-Authenticate": "Bearer"})
async def refresh_access_token(
        current_user: Annotated[User, Depends(get_current_user)],
) -> Token:
    """
    刷新访问令牌

    该函数接收一个访问令牌，并使用它来生成一个新的访问令牌。
    如果访问令牌无效或已过期，将抛出HTTP 401未授权异常。

    - param token: 访问令牌
    - return: 刷新后的访问令牌
    - raises HTTPException: 当访问令牌无效或已过期时抛出401未授权异常
    """
    access_token = create_access_token(data={"sub": json.dumps(current_user)})
    return Token(data={"access_token": access_token, "token_type": "Bearer"})
