from app.main import app
from app.providers.parking.factory import get_parking_provider
from app.providers.parking.mock import MockFailure, MockParkingProvider
from httpx import AsyncClient


async def create_vehicle_and_zone(client: AsyncClient, headers: dict[str, str]) -> tuple[str, str]:
    vehicle = await client.post(
        "/api/v1/vehicles",
        headers=headers,
        json={
            "plate_number": "А123АА",
            "region_code": "23",
            "display_name": "Toyota RAV4",
        },
    )
    nearby = await client.get(
        "/api/v1/parking/nearby",
        headers=headers,
        params={"latitude": 45.03547, "longitude": 38.97531, "radius": 1500},
    )
    assert nearby.status_code == 200, nearby.text
    return vehicle.json()["id"], nearby.json()["zones"][0]["id"]


async def test_start_duplicate_stop_history_and_stats(
    client: AsyncClient, authenticated: tuple[dict[str, str], dict[str, object]]
) -> None:
    headers, _ = authenticated
    vehicle_id, zone_id = await create_vehicle_and_zone(client, headers)
    body = {"vehicle_id": vehicle_id, "parking_zone_id": zone_id}

    started = await client.post("/api/v1/parking/sessions", headers=headers, json=body)
    assert started.status_code == 201, started.text
    session_id = started.json()["id"]
    assert started.json()["status"] == "active"

    duplicate = await client.post("/api/v1/parking/sessions", headers=headers, json=body)
    assert duplicate.status_code == 409
    assert duplicate.json()["error"]["code"] == "SESSION_ALREADY_ACTIVE"

    current = await client.get("/api/v1/parking/sessions/current", headers=headers)
    assert current.status_code == 200
    assert current.json()["id"] == session_id

    blocked_delete = await client.delete(f"/api/v1/vehicles/{vehicle_id}", headers=headers)
    assert blocked_delete.status_code == 409
    assert blocked_delete.json()["error"]["code"] == "VEHICLE_IN_ACTIVE_SESSION"

    stopped = await client.post(f"/api/v1/parking/sessions/{session_id}/stop", headers=headers)
    assert stopped.status_code == 200, stopped.text
    assert stopped.json()["status"] == "completed"
    assert stopped.json()["payment_status"] == "paid"

    current_after = await client.get("/api/v1/parking/sessions/current", headers=headers)
    assert current_after.status_code == 200
    assert current_after.json() is None
    history = await client.get("/api/v1/parking/history", headers=headers)
    assert history.json()["sessions"][0]["id"] == session_id
    stats = await client.get("/api/v1/parking/stats", headers=headers)
    assert stats.json()["parking_count"] == 1


async def test_provider_unavailable_is_mapped(
    client: AsyncClient, authenticated: tuple[dict[str, str], dict[str, object]]
) -> None:
    headers, _ = authenticated
    failing = MockParkingProvider(latency_seconds=0)
    failing.failure = MockFailure.UNAVAILABLE
    app.dependency_overrides[get_parking_provider] = lambda: failing
    try:
        response = await client.get(
            "/api/v1/parking/nearby",
            headers=headers,
            params={"latitude": 45.03547, "longitude": 38.97531, "radius": 1500},
        )
        assert response.status_code == 503
        assert response.json()["error"]["code"] == "PROVIDER_UNAVAILABLE"
    finally:
        app.dependency_overrides.clear()


async def test_invalid_zone_and_payment_failure(
    client: AsyncClient, authenticated: tuple[dict[str, str], dict[str, object]]
) -> None:
    headers, _ = authenticated
    vehicle_id, zone_id = await create_vehicle_and_zone(client, headers)
    bad = await client.post(
        "/api/v1/parking/sessions",
        headers=headers,
        json={"vehicle_id": vehicle_id, "parking_zone_id": "00000000-0000-0000-0000-000000000000"},
    )
    assert bad.status_code == 404

    failing = MockParkingProvider(latency_seconds=0)
    app.dependency_overrides[get_parking_provider] = lambda: failing
    try:
        started = await client.post(
            "/api/v1/parking/sessions",
            headers=headers,
            json={"vehicle_id": vehicle_id, "parking_zone_id": zone_id},
        )
        assert started.status_code == 201, started.text
        failing.failure = MockFailure.PAYMENT_FAILED
        stopped = await client.post(
            f"/api/v1/parking/sessions/{started.json()['id']}/stop", headers=headers
        )
        assert stopped.status_code == 402
        assert stopped.json()["error"]["code"] == "PAYMENT_FAILED"
        current = await client.get("/api/v1/parking/sessions/current", headers=headers)
        assert current.json() is None
    finally:
        app.dependency_overrides.clear()
