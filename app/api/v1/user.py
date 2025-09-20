from datetime import timedelta
import re
from typing import Annotated
from fastapi import APIRouter, Body, HTTPException, status
from pydantic import BaseModel, Field, field_validator

from app.core.config import settings
from app.core.database import DataBaseSessionDepency
from app.core.security import Token, create_access_token
from app.models.sql.user import User
from app.services.user_service import user_service

user_router = APIRouter(prefix="/user", tags=["user"])


class UserRegister(BaseModel):
    username: str
    password: str
    email: str = Field(..., pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    avatar: str = ''

    @field_validator('username')
    def validate_username(cls, username):
        if len(username) < 3:
            raise ValueError('用户名长度至少为3个字符')
        if len(username) > 20:
            raise ValueError('用户名长度不能超过20个字符')
        if not re.match(r'^[a-zA-Z0-9_\u4e00-\u9fa5]+$', username):
            raise ValueError('用户名只能包含字母、数字、下划线和中文字符')
        return username

    @field_validator('password')
    def validate_password(cls, password):
        if len(password) < 6:
            raise ValueError('密码长度至少为6个字符')
        return password
    model_config = {
        "json_schema_extra": {
            "example": {
                "username": "test",
                "password": "password",
                "email": "test@example.com",
                "avatar": ""
            }
        }
    }


class UserLogin(BaseModel):
    username: str
    password: str


@user_router.post('/register', response_model=User)
async def register(user: Annotated[UserRegister, Body()],database: DataBaseSessionDepency):
    """
    用户注册接口
    
    - **username**: 用户名，3-20个字符，只能包含字母、数字、下划线和中文
    - **password**: 密码，至少6个字符
    - **email**: 邮箱地址，需符合标准邮箱格式
    - **avatar**: 头像URL，可选
    
    返回创建的用户信息
    """
    try:
        db_user = await user_service.create_user(
            db=database,
            username=user.username,
            email=user.email,
            password=user.password,
            avatar=user.avatar
        )
        return db_user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
@user_router.post('/login',response_model=Token)
async def login(user: Annotated[UserLogin, Body()], database: DataBaseSessionDepency):
    """
    用户登录接口
    
    - **username**: 用户名
    - **password**: 密码
    
    返回访问令牌
    """
    error =HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

    try:
        db_user = await user_service.authenticate_user(
            db=database,
            username=user.username,
            password=user.password
        )
        if db_user:
            access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(
                data={"sub": db_user.username}, expires_delta=access_token_expires
            )
            return Token(access_token=access_token, token_type="bearer")
        else:
            raise error
        
    except ValueError as e:
        raise error
