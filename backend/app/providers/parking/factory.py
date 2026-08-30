from functools import lru_cache

from app.core.config import get_settings
from app.providers.parking.base import ParkingProvider
from app.providers.parking.mock import MockParkingProvider
from app.providers.parking.parkomatika import ParkomatikaProvider


@lru_cache
def get_parking_provider() -> ParkingProvider:
    settings = get_settings()
    if settings.PARKING_PROVIDER == "parkomatika":
        return ParkomatikaProvider()
    latency = 0.0 if settings.PRESENTATION_MODE or settings.TESTING else 0.05
    return MockParkingProvider(latency_seconds=latency)
