import json
from nt import access
from typing import Annotated

from fastapi import APIRouter, Depends, Header, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import exc
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core import wrap_error_handler_api
from app.core.config import settings
from app.core.database import get_session
from app.core.error_handler import CustomException
from app.core.security import create_access_token, create_refresh_token, get_current_user
from app.models.response_model import ResponseModel
from app.models.sql.User import User
from app.services import user_service
from app.services.cache_service import cache_delete, cache_get, cache_set
from app.services.user_service import UserService

token_router = APIRouter(prefix='/token', tags=["token"])


class TokenData(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class Token(ResponseModel):
    """
    令牌模型
    - data
    - - access_token (str): 访问令牌
    - - token_type (str): 令牌类型
    """
    data: TokenData


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
    content = json.dumps({
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "avatar": user.avatar,
        "is_active": user.is_active,
    })
    access_token = create_access_token(
        data={"sub": content}
    )
    refresh_token = create_refresh_token()
    is_cached = await cache_set(
        args=[],
        kwargs={},
        value=content,
        key_prefix=f'{refresh_token}',
        expire=settings.REFRESH_TOKEN_EXPIRE
    )
    if not is_cached:
        raise CustomException(
            message='服务器内部错误，请稍后重试'
        )
    return Token(
        data=TokenData(
            access_token=access_token,
            refresh_token=refresh_token,
        )
    )


@token_router.post('/refresh', response_model=Token)
@wrap_error_handler_api(status_code=status.HTTP_401_UNAUTHORIZED, headers={"WWW-Authenticate": "Bearer"})
async def refresh_access_token(
        Authorization: Annotated[str, Header(name='Authorization')]
) -> Token:
    """
    刷新访问令牌

    该函数接收一个刷新访问令牌，并使用它来生成一个新的访问令牌。
    - param token: 访问令牌
    - return: 刷新后的访问令牌
    """
    error = CustomException(
        message='请先登录',
        status_code=status.HTTP_401_UNAUTHORIZED,
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not Authorization or not Authorization.startswith('Bearer '):
        raise error
    refresh_token = Authorization.split(' ')[1]
    user = await cache_get(
        args=[],
        kwargs={},
        key_prefix=f'{refresh_token}'
    )
    if not user:
        raise error
    else:
        await cache_delete(
            args=[],
            kwargs={},
            key_prefix=f'{refresh_token}'
        )
        access_token = create_access_token(
            data={"sub": user}
        )
        refresh_token = create_refresh_token()
        is_cached = await cache_set(
            args=[],
            kwargs={},
            value=user,
            key_prefix=f'{refresh_token}',
            expire=settings.REFRESH_TOKEN_EXPIRE
        )
        if not is_cached:
            raise CustomException(
                message='服务器内部错误，请稍后重试'
            )
        return Token(
            data=TokenData(
                access_token=access_token,
                refresh_token=refresh_token,
            )
        )
