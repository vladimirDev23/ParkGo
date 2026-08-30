from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest
from app.exceptions.domain import InvalidZoneError, ProviderUnavailableError
from app.providers.parking.mock import MockFailure, MockParkingProvider


async def test_nearest_zone_and_price_calculation() -> None:
    provider = MockParkingProvider(latency_seconds=0)
    zones = await provider.get_nearby_zones(45.03547, 38.97531, 1500)
    assert len(zones) >= 5
    assert zones[0].zone_number == "1001"
    assert zones == sorted(zones, key=lambda zone: zone.distance_meters or 0)

    started = datetime(2026, 8, 30, 10, tzinfo=UTC)
    price = await provider.calculate_price(
        "demo-1001", "А123АА 23", started, started + timedelta(minutes=61)
    )
    assert price.amount == Decimal("61.00")


async def test_provider_error_modes() -> None:
    provider = MockParkingProvider(latency_seconds=0)
    with pytest.raises(InvalidZoneError):
        await provider.get_zone("missing")

    provider.failure = MockFailure.UNAVAILABLE
    with pytest.raises(ProviderUnavailableError):
        await provider.get_nearby_zones(45.0, 39.0, 1000)
