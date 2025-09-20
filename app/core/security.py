from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from pydantic import BaseModel
# 导入数据库相关
from sqlmodel import select

from app.core.config import settings
from app.core.database import DataBaseSessionDepency
from app.models.sql.user import User

# 解决bcrypt版本兼容性问题
try:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
except Exception as e:
    print(f"INFO - Failed to initialize bcrypt context: {e}")
    # 降级到使用sha256_crypt作为替代方案
    pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class Token(BaseModel):
    access_token: str
    token_type: str

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


async def authenticate_user(username: str, password: str,db: DataBaseSessionDepency):
    statement = select(User).where(User.username == username)
    result = await db.exec(statement)
    user = result.first()
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user: str = payload.get("sub")
        if user is None:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception
    
    # 这里应该从数据库获取用户
    # 简化处理，直接返回用户名
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    """
    判断用户是否激活，如果未激活则抛出HTTP 400异常
    :param current_user:  当前用户
    :return:    当前用户
    """
    if current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

from fastapi import  APIRouter
token_router =  APIRouter(prefix='/token', tags=["token"])

@token_router.post('/get', response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    database: DataBaseSessionDepency
) -> Token:
    """
    处理用户登录请求并生成访问令牌
    
    该函数接收用户名和密码，验证用户身份后生成JWT访问令牌。
    如果认证失败，将抛出HTTP 401未授权异常。
    
    - param form_data: OAuth2密码请求表单数据，包含用户名和密码
    - return: 包含访问令牌和令牌类型的Token对象
    - raises HTTPException: 当用户名或密码不正确时抛出401未授权异常
    """

    user_dict = {"username": form_data.username, "password": form_data.password}
    user = await authenticate_user(db=database,**user_dict)
    if type(user) is bool and not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user_dict["username"]}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")

@token_router.post('/refresh', response_model=Token)
async def refresh_access_token(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> Token:
    """
    刷新访问令牌

    该函数接收一个访问令牌，并使用它来生成一个新的访问令牌。
    如果访问令牌无效或已过期，将抛出HTTP 401未授权异常。

    - param token: 访问令牌
    - return: 刷新后的访问令牌
    - raises HTTPException: 当访问令牌无效或已过期时抛出401未授权异常
    """
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": current_user.username},expires_delta=access_token_expires)
    return Token(access_token=access_token, token_type="bearer")
