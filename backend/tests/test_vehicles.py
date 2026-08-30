from httpx import AsyncClient


async def test_vehicle_crud_and_default_selection(
    client: AsyncClient, authenticated: tuple[dict[str, str], dict[str, object]]
) -> None:
    headers, _ = authenticated
    first = await client.post(
        "/api/v1/vehicles",
        headers=headers,
        json={
            "plate_number": "а123аа",
            "region_code": "23",
            "display_name": "Toyota RAV4",
        },
    )
    assert first.status_code == 201, first.text
    first_data = first.json()
    assert first_data["plate_number"] == "А123АА"
    assert first_data["is_default"] is True

    second = await client.post(
        "/api/v1/vehicles",
        headers=headers,
        json={
            "plate_number": "B456CC",
            "region_code": "93",
            "display_name": "Volvo XC60",
        },
    )
    assert second.status_code == 201
    second_id = second.json()["id"]

    made_default = await client.post(f"/api/v1/vehicles/{second_id}/default", headers=headers)
    assert made_default.status_code == 200
    assert made_default.json()["is_default"] is True

    changed = await client.patch(
        f"/api/v1/vehicles/{second_id}",
        headers=headers,
        json={"color": "Синий"},
    )
    assert changed.status_code == 200
    assert changed.json()["color"] == "Синий"

    deleted = await client.delete(f"/api/v1/vehicles/{second_id}", headers=headers)
    assert deleted.status_code == 204
    vehicles = (await client.get("/api/v1/vehicles", headers=headers)).json()
    assert len(vehicles) == 1
    assert vehicles[0]["is_default"] is True
