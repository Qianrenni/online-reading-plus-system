from datetime import timedelta, timezone,datetime
from typing import Annotated, Any
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from app.core.config import settings
from app.middleware.logging import logger
from app.models.sql.user import User

# 解决bcrypt版本兼容性问题
try:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
except Exception as e:
    logger.info(f"INFO - Failed to initialize bcrypt context: {e}")
    # 降级到使用sha256_crypt作为替代方案
    pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token/get")

def verify_password(plain_password: str , hashed_password: str ):
    """
    验证密码是否正确
    Args:
        plain_password (str): 明文密码
        hashed_password (str): 密码哈希值
    Returns:
        bool: 如果密码正确，则返回True，否则返回False
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password:str):
    """
    获取密码哈希值
    Args:
        password (str): 密码
    Returns:
        str: 密码哈希值
    """
    return pwd_context.hash(password)

def create_access_token(data: dict[str,Any], expires_delta: timedelta | None = None):
    """
    创建访问令牌
    Args:
        data (dict[str,Any]): 令牌数据
        expires_delta (timedelta | None, optional): 令牌过期时间. Defaults to None.
    Returns:
        str: 令牌字符串
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    """
    获取当前用户
    该函数接收一个访问令牌，并使用它来验证用户身份。
    如果访问令牌无效或已过期，将抛出HTTP 401未授权异常。
    - param token: 访问令牌
    - return: 当前用户
    - raises HTTPException: 当访问令牌无效或已过期时抛出401未授权异常
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user: str = payload.get("sub")
        if not user:
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