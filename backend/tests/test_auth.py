from httpx import AsyncClient


async def test_register_login_me_and_refresh_rotation(client: AsyncClient) -> None:
    registration = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "person@example.com",
            "password": "SecurePass123!",
            "first_name": "Анна",
        },
    )
    assert registration.status_code == 201
    registered = registration.json()
    assert registered["user"]["email"] == "person@example.com"

    me = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {registered['access_token']}"},
    )
    assert me.status_code == 200
    assert me.json()["first_name"] == "Анна"

    refreshed = await client.post(
        "/api/v1/auth/refresh", json={"refresh_token": registered["refresh_token"]}
    )
    assert refreshed.status_code == 200
    assert refreshed.json()["refresh_token"] != registered["refresh_token"]

    replay = await client.post(
        "/api/v1/auth/refresh", json={"refresh_token": registered["refresh_token"]}
    )
    assert replay.status_code == 401
    assert replay.json()["error"]["code"] == "AUTHENTICATION_REQUIRED"

    login = await client.post(
        "/api/v1/auth/login",
        json={"email": "person@example.com", "password": "SecurePass123!"},
    )
    assert login.status_code == 200


async def test_auth_errors_have_safe_envelope(client: AsyncClient) -> None:
    invalid = await client.post(
        "/api/v1/auth/login",
        json={"email": "missing@example.com", "password": "wrong"},
    )
    assert invalid.status_code == 401
    assert invalid.json() == {
        "error": {
            "code": "INVALID_CREDENTIALS",
            "message": "Неверный email или пароль.",
            "details": {},
        }
    }

    validation = await client.post(
        "/api/v1/auth/register", json={"email": "not-email", "password": "short"}
    )
    assert validation.status_code == 422
    assert validation.json()["error"]["code"] == "VALIDATION_ERROR"
