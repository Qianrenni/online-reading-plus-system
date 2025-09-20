from typing import Optional
from sqlmodel import select
from sqlalchemy.exc import IntegrityError

from app.core.database import DataBaseSessionDepency
from app.models.sql.user import User
from app.core.security import get_password_hash, verify_password


class UserService:
    """
    用户服务类，处理用户相关的业务逻辑
    """

    @staticmethod
    async def create_user(
        db: DataBaseSessionDepency,
        username: str,
        email: str,
        password: str,
        avatar: str = ""
    ) -> User:
        """
        创建新用户

        Args:
            db: 数据库会话依赖
            username: 用户名
            email: 邮箱
            password: 明文密码
            avatar: 头像URL

        Returns:
            User: 创建的用户对象，包含数据库自动生成的ID

        Raises:
            ValueError: 当用户名或邮箱已存在时抛出
        """
        # 检查用户名是否已存在
        statement = select(User).where(User.username == username)
        result = await db.exec(statement)
        if result.first():
            raise ValueError("用户名已存在")

        # 检查邮箱是否已存在
        statement = select(User).where(User.email == email)
        result = await db.exec(statement)
        if result.first():
            raise ValueError("邮箱已被注册")

        # 创建新用户
        hashed_password = get_password_hash(password)
        db_user = User(
            username=username,
            password=hashed_password,
            email=email,
            avatar=avatar
        )

        try:
            db.add(db_user)
            await db.commit()
            await db.refresh(db_user)
            return db_user
        except IntegrityError:
            await db.rollback()
            raise ValueError("用户创建失败，可能用户名或邮箱已存在")
            
    @staticmethod
    async def authenticate_user(
        db: DataBaseSessionDepency,
        username: str,
        password: str
    ) -> User|None:
        """
        验证用户凭据
        
        Args:
            db: 数据库会话依赖
            username: 用户名
            password: <PASSWORD>

        Returns:
            User|None: 如果凭据有效，则返回用户对象，否则返回None

        Raises:
            ValueError: 当用户名或密码无效时抛出
        """
        statement = select(User).where(User.username == username)
        result = await db.exec(statement)
        user = result.first()
        if not user:
            raise ValueError("用户名或密码无效")
        if verify_password(password, user.password):
            return user
        else:
            raise ValueError("用户名或密码无效")

user_service = UserService()