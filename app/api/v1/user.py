import re
from typing import Annotated

from fastapi import APIRouter, Body, HTTPException, status, Depends, Header
from pydantic import BaseModel, Field, field_validator
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core import wrap_error_handler_api
from app.core.database import get_session
from app.core.error_handler import CustomException
from app.services.cache_service import cache_get, cache_delete
from app.services.captcha_service import CaptchaService
from app.services.user_service import user_service

user_router = APIRouter(prefix="/user", tags=["user"])


class UserRegister(BaseModel):
    username: str
    password: str
    email: str = Field(..., pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    avatar: str = ''

    @field_validator('username')
    def validate_username(cls,username: str):
        if len(username) < 3:
            raise ValueError('用户名长度至少为3个字符')
        if len(username) > 20:
            raise ValueError('用户名长度不能超过20个字符')
        if not re.match(r'^[a-zA-Z0-9_\u4e00-\u9fa5]+$', username):
            raise ValueError('用户名只能包含字母、数字、下划线和中文字符')
        return username

    @field_validator('password')
    def validate_password(cls,password: str):
        if len(password) < 6:
            raise ValueError('密码长度至少为6个字符')
        return password


@user_router.post('/register', status_code=status.HTTP_201_CREATED)
@wrap_error_handler_api()
async def register(
        user: Annotated[UserRegister, Body()],
        database: Annotated[AsyncSession, Depends(get_session)],
        captcha: Annotated[str, Body(embed=True)],
        x_captcha_id: Annotated[str, Header(name='X-Captcha-Id')]
):
    """
    用户注册接口
    
    - **username**: 用户名，3-20个字符，只能包含字母、数字、下划线和中文
    - **password**: 密码，至少6个字符
    - **email**: 邮箱地址，需符合标准邮箱格式
    - **avatar**: 头像URL，可选
    
    返回创建的用户信息
    """
    key_prefix = f'email_verified:{user.email}'
    if not await CaptchaService.verify_captcha(captcha_id=x_captcha_id, captcha_text=captcha):
        raise CustomException(status_code=status.HTTP_400_BAD_REQUEST, message='验证码错误')
    is_verify_email = await cache_get(key_prefix=key_prefix)
    if not is_verify_email:
        raise CustomException(status_code=status.HTTP_400_BAD_REQUEST, message='邮箱未验证')
    await user_service.create_user(
        db=database,
        username=user.username,
        email=user.email,
        password=user.password,
        avatar=user.avatar
    )
    await cache_delete(key_prefix=key_prefix)
    return


class UserPasswordUpdate(BaseModel):
    """
    用户密码更新模型
    - **username**: 邮箱地址
    - **password**: 当前密码
    - **new_password**: 新密码
    """
    username: str
    old_password: str
    new_password: str


@user_router.patch('/update-password', status_code=status.HTTP_204_NO_CONTENT)
@wrap_error_handler_api()
async def update_user(
        user: Annotated[UserPasswordUpdate, Body()],
        database: Annotated[AsyncSession, Depends(get_session)]
):
    """
    更新用户密码
    
    - **username**: 用户名
    - **password**: 当前密码
    - **new_password**: 新密码
    
    返回更新后的用户信息
    """
    result = await user_service.update_password(
        db=database,
        user_email=user.username,
        old_password=user.old_password,
        new_password=user.new_password,
    )
    if result:
        return
