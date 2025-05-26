from pydantic import AfterValidator, BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Any, Annotated
import os


def _parse_list(v: Any) -> list[str]:
    return list(map(str, v.split(",")))


class BaseConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="env/.env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        env_ignore_empty=True,
        extra="ignore",
    )


list_str = Annotated[list[str], AfterValidator(_parse_list)]


class _DBConfig(BaseConfig):
    POSTGRES_USER: str = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD")
    DB_HOST: str = os.getenv("DB_HOST")
    DB_PORT: int = os.getenv("DB_PORT")
    DB_DATABASE: str = os.getenv("DB_DATABASE")

    @property
    def url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}"
            f"/{self.DB_DATABASE}"
        )


# class _RedisConfig(BaseConfig):
#     REDIS_HOST: str = os.getenv("REDIS_HOST")
#     REDIS_PORT: int = os.getenv("REDIS_PORT")
#     REDIS_DATABASE: str = os.getenv("REDIS_DATABASE")

#     @property
#     def url(self) -> str:
#         return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DATABASE}"


# class _ApiConfig(BaseModel):
#     CORS_ORIGINS: list_str = os.getenv("CORS_ORIGINS")
#     CORS_CREDENTIALS: bool = os.getenv("CORS_CREDENTIALS")
#     CORS_METHODS: list_str = os.getenv("CORS_METHODS")
#     CORS_HEADERS: list_str = os.getenv("CORS_HEADERS")
#     MODE: str = os.getenv("MODE")


# class _RMQConfig(BaseConfig):
#     RMQ_USERNAME: str = os.getenv("RMQ_USERNAME")
#     RMQ_PASSWORD: str = os.getenv("RMQ_PASSWORD")
#     RMQ_HOST: str = os.getenv("RMQ_HOST")
#     RMQ_PORT: int = os.getenv("RMQ_PORT")

#     @property
#     def url(self) -> str:
#         return (
#             f"amqp://{self.RMQ_USERNAME}:{self.RMQ_PASSWORD}"
#             f"@{self.RMQ_HOST}:{self.RMQ_PORT}"
#         )


class _LoggingConfig(BaseConfig):
    FORMAT: str = os.getenv("FORMAT")


class _Config:
    def __init__(self) -> None:
        self.db = _DBConfig()
        # self.redis = _RedisConfig()
        # self.api = _ApiConfig()
        # self.rmq = _RMQConfig()
        self.log = _LoggingConfig()


config = _Config()
