from datetime import datetime, timedelta
from typing import Optional
import jwt
from jwt import PyJWTError
from passlib.context import CryptContext
from app.config.settings import settings

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT相关配置
ALGORITHM = settings.algorithm
SECRET_KEY = settings.secret_key
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes


def verify_password(plain_password, hashed_password):
    """
    验证明文密码与哈希密码是否匹配
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    """
    对密码进行哈希处理
    """
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    创建访问令牌
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def authenticate_user(db, username: str, password: str):
    """
    验证用户身份
    """
    # 这里需要从数据库获取用户信息
    # user = await get_user_by_username(db, username)
    # if not user:
    #     return False
    # if not verify_password(password, user.hashed_password):
    #     return False
    # return user
    pass


async def get_password_reset_token(db, email: str):
    """
    获取密码重置令牌
    """
    # 生成密码重置token并保存到数据库
    pass