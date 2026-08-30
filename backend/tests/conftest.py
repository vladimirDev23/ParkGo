import os
from collections.abc import AsyncIterator

os.environ.update(
    {
        "APP_ENV": "test",
        "TESTING": "true",
        "AUTO_CREATE_SCHEMA": "true",
        "PRESENTATION_MODE": "false",
        "SECRET_KEY": "test-secret-key-with-more-than-thirty-two-characters",
        "DATABASE_URL": "sqlite+aiosqlite:///./parkgo-test.db",
        "REDIS_URL": "redis://127.0.0.1:6399/15",
        "AUTH_RATE_LIMIT": "1000",
    }
)

import pytest
from app.db.base import Base
from app.db.session import SessionFactory, engine
from app.main import app
from app.providers.parking.mock import ZONE_FIXTURES
from app.repositories.parking import ZoneRepository
from httpx import ASGITransport, AsyncClient


@pytest.fixture(autouse=True)
async def reset_database() -> AsyncIterator[None]:
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)
    async with SessionFactory() as session:
        await ZoneRepository(session).sync(list(ZONE_FIXTURES))
        await session.commit()
    yield


@pytest.fixture
async def client() -> AsyncIterator[AsyncClient]:
    async with AsyncClient(
        transport=ASGITransport(app=app, raise_app_exceptions=False),
        base_url="http://test",
    ) as http_client:
        yield http_client


@pytest.fixture
async def authenticated(client: AsyncClient) -> tuple[dict[str, str], dict[str, object]]:
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "driver@example.com",
            "password": "SecurePass123!",
            "first_name": "Иван",
        },
    )
    assert response.status_code == 201, response.text
    payload = response.json()
    return {"Authorization": f"Bearer {payload['access_token']}"}, payload
