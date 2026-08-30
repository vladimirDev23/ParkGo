from datetime import datetime, timedelta
from decimal import Decimal

from app.exceptions.domain import ProviderUnavailableError
from app.providers.parking.base import ParkingProvider
from app.providers.parking.dto import ParkingZoneDTO, PriceDTO, ProviderSessionDTO


class ParkomatikaProvider(ParkingProvider):
    """Authorized Parkomatika adapter placeholder.

    TODO: implement only after official API documentation, sandbox access,
    credentials, state semantics and commercial authorization are supplied.
    No endpoint names or parameters are assumed here.
    """

    name = "parkomatika"

    def _unavailable(self) -> ProviderUnavailableError:
        return ProviderUnavailableError("Интеграция с Паркоматикой ещё не настроена.")

    async def get_nearby_zones(
        self, latitude: float, longitude: float, radius_meters: int
    ) -> list[ParkingZoneDTO]:
        raise self._unavailable()

    async def get_zone(self, external_zone_id: str) -> ParkingZoneDTO:
        raise self._unavailable()

    async def calculate_price(
        self,
        zone_id: str,
        vehicle_plate: str,
        started_at: datetime,
        finished_at: datetime,
    ) -> PriceDTO:
        raise self._unavailable()

    async def start_session(
        self, zone_id: str, vehicle_plate: str, started_at: datetime
    ) -> ProviderSessionDTO:
        raise self._unavailable()

    async def stop_session(
        self, provider_session_id: str, finished_at: datetime
    ) -> ProviderSessionDTO:
        raise self._unavailable()

    async def extend_session(
        self, provider_session_id: str, duration: timedelta
    ) -> ProviderSessionDTO:
        raise self._unavailable()

    async def get_session(self, provider_session_id: str) -> ProviderSessionDTO:
        raise self._unavailable()

    async def process_payment(self, provider_session_id: str, amount: Decimal) -> str:
        raise self._unavailable()
