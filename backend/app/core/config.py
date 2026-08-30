from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    APP_NAME: str = "ParkGo API"
    APP_ENV: Literal["development", "test", "production"] = "development"
    DEBUG: bool = False
    API_PREFIX: str = "/api/v1"
    SECRET_KEY: SecretStr = SecretStr("local-development-secret-change-me")
    ACCESS_TOKEN_MINUTES: int = 15
    REFRESH_TOKEN_DAYS: int = 30
    JWT_ALGORITHM: str = "HS256"
    DATABASE_URL: str = "postgresql+asyncpg://parkgo:parkgo@localhost:5432/parkgo"
    REDIS_URL: str = "redis://localhost:6379/0"
    CORS_ORIGINS: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])
    PARKING_PROVIDER: Literal["mock", "parkomatika"] = "mock"
    PRESENTATION_MODE: bool = False
    AUTO_CREATE_SCHEMA: bool = False
    TESTING: bool = False
    SENTRY_DSN: str | None = None
    AUTH_RATE_LIMIT: int = 10
    AUTH_RATE_WINDOW_SECONDS: int = 60
    PROVIDER_TIMEOUT_SECONDS: float = 5.0

    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret(cls, value: SecretStr, info: object) -> SecretStr:
        if len(value.get_secret_value()) < 32:
            raise ValueError("SECRET_KEY must contain at least 32 characters")
        return value

    def validate_production(self) -> None:
        if self.APP_ENV != "production":
            return
        if self.DEBUG or self.PRESENTATION_MODE or self.AUTO_CREATE_SCHEMA:
            raise RuntimeError("Unsafe development flags are enabled in production")
        if "change-me" in self.SECRET_KEY.get_secret_value():
            raise RuntimeError("A production SECRET_KEY must be supplied")
        if not self.DATABASE_URL.startswith("postgresql+asyncpg://"):
            raise RuntimeError("Production requires PostgreSQL")


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.validate_production()
    return settings
