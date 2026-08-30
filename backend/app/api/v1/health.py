from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel
from redis.asyncio import Redis
from redis.exceptions import RedisError
from sqlalchemy import text

from app.api.dependencies import AppSettings, DbSession

router = APIRouter(tags=["Operations"])


class HealthResponse(BaseModel):
    status: Literal["ok", "degraded"]
    database: Literal["ok", "unavailable"]
    redis: Literal["ok", "unavailable"]
    provider: str
    test_mode: bool


@router.get("/health", response_model=HealthResponse)
async def health(session: DbSession, settings: AppSettings) -> HealthResponse:
    database_status: Literal["ok", "unavailable"] = "ok"
    redis_status: Literal["ok", "unavailable"] = "ok"
    try:
        await session.execute(text("SELECT 1"))
    except Exception:
        database_status = "unavailable"
    redis = Redis.from_url(settings.REDIS_URL)
    try:
        await redis.ping()
    except RedisError:
        redis_status = "unavailable"
    finally:
        await redis.aclose()
    status_value: Literal["ok", "degraded"] = "ok" if database_status == "ok" else "degraded"
    return HealthResponse(
        status=status_value,
        database=database_status,
        redis=redis_status,
        provider=settings.PARKING_PROVIDER,
        test_mode=settings.PARKING_PROVIDER == "mock",
    )
