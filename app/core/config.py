# app/core/config.py
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Online Reading System"
    ENV: str = "development"
    PROTOCOL: str
    # Database
    MYSQL_DSN: str
    REDIS_URL: str

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # 分表
    BOOK_SHARD_COUNT: int = 64

    #  书籍缓存
    BOOK_CACHE_EXPIRE: int =  60 * 60 * 24 * 7
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()