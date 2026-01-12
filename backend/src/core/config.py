from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.core.constants import Environment


class CustomBaseSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

class Settings(CustomBaseSettings):
    # Database
    DATABASE_URL: PostgresDsn
    DATABASE_POOL_SIZE: int = 16
    DATABASE_POOL_TTL: int = 60 * 20  # 20 minutes
    DATABASE_POOL_PRE_PING: bool = True
    
    CORS_ORIGINS: list[str] = ["*"]
    CORS_ORIGINS_REGEX: str | None = None
    CORS_HEADERS: list[str] = ["*"]
    FRONTEND_URL: str = "http://localhost:5173"
    
    POSTGRES_USER: str
    POSTGRES_DB: str
    POSTGRES_PASSWORD: str
    POSTGRES_PORT: str
    POSTGRES_HOST: str

    # Authentication
    SECRET_KEY: str
    SECURITY_ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRES: int
    VERIFY_TOKEN_EXPIRES: int

settings = Settings() 