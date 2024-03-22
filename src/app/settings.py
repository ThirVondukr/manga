import enum
from collections.abc import Sequence
from datetime import timedelta
from types import SimpleNamespace
from typing import Literal
from urllib.parse import quote_plus

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

_MEGABYTES = 1024 * 1024


class SentryEnvironment(enum.StrEnum):
    development = enum.auto()
    staging = enum.auto()
    production = enum.auto()


class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="database_")

    driver: str = "postgresql+asyncpg"
    name: str
    username: str
    password: str
    host: str

    echo: bool = False

    @property
    def url(self) -> str:
        password = quote_plus(self.password)
        return f"{self.driver}://{self.username}:{password}@{self.host}/{self.name}"


class SentrySettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="sentry_")

    dsn: str = ""
    environment: SentryEnvironment = SentryEnvironment.production
    traces_sample_rate: float = Field(default=1.0, ge=0.0, le=1.0)


class AuthSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="auth_")

    algorithm: Literal["RS256"] = "RS256"
    public_key: str
    private_key: str
    access_token_lifetime: timedelta = timedelta(minutes=15)
    refresh_token_lifetime: timedelta = timedelta(days=3)
    refresh_token_cookie: str = "refresh-token"

    hashing_schemes: list[str] = ["argon2"]


class S3Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="s3_")

    public_url: str
    endpoint_url: str
    access_key: str
    secret_key: str

    bucket: str = "manga"

    multipart_upload_chunk_size: int = 5 * _MEGABYTES


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="app_")

    cors_allow_origins: list[str] = []
    cors_allow_methods: list[str] = ["*"]
    cors_allow_headers: list[str] = ["authorization"]

    max_upload_size_bytes: int = 250 * _MEGABYTES
    max_concurrent_uploads: int = 5


class ImageSettings(BaseSettings):
    default_src_set: Sequence[int] = (128, 256, 384, 640, 896, 1200)
    manga_page_src_set: Sequence[int] = (400, 640)
    thumbnail_image_format: Literal["webp"] = "webp"
    thumbnail_quality: int = 90


class ImagePaths(SimpleNamespace):
    chapter_images = "chapters"
    manga_arts = "manga-art"
