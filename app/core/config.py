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
    # ACCESS_TOKEN_EXPIRE_有效期
    ACCESS_TOKEN_EXPIRE: int = 30 * 60 * 60
    # refresh_token 有效期
    REFRESH_TOKEN_EXPIRE: int = 7 * 24 * 60 * 60
    # 邮箱验证 有效期
    EMAIL_VERIFY_EXPIRE: int = 5 * 60
    #  验证码 有效期
    CAPTCHA_EXPIRE: int = 2 * 60
    # 分表
    BOOK_SHARD_COUNT: int = 64

    #  书籍缓存
    BOOK_CACHE_EXPIRE: int = 60 * 60 * 24 * 7
    # SERVER_URL
    SERVER_URL: str = "http://127.0.0.1:8000"
    # 邮箱授权码
    EMAIL_CODE: str
    # 邮箱账号
    EMAIL_ACCOUNT: str

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
