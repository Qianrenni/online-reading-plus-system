from pydantic import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # 数据库配置
    database_url: str = "mysql+aiomysql://user:password@localhost:3306/reading_system"
    redis_url: str = "redis://localhost:6379/0"
    mongodb_url: str = "mongodb://localhost:27017/reading_system"

    # JWT配置
    secret_key: str = "your_secret_key_here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # 支付宝配置
    alipay_app_id: str = ""
    alipay_private_key: str = ""
    alipay_public_key: str = ""

    class Config:
        env_file = ".env"


settings = Settings()
