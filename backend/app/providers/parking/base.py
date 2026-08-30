from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from decimal import Decimal

from app.providers.parking.dto import ParkingZoneDTO, PriceDTO, ProviderSessionDTO


class ParkingProvider(ABC):
    name: str

    @abstractmethod
    async def get_nearby_zones(
        self, latitude: float, longitude: float, radius_meters: int
    ) -> list[ParkingZoneDTO]: ...

    @abstractmethod
    async def get_zone(self, external_zone_id: str) -> ParkingZoneDTO: ...

    @abstractmethod
    async def calculate_price(
        self,
        zone_id: str,
        vehicle_plate: str,
        started_at: datetime,
        finished_at: datetime,
    ) -> PriceDTO: ...

    @abstractmethod
    async def start_session(
        self, zone_id: str, vehicle_plate: str, started_at: datetime
    ) -> ProviderSessionDTO: ...

    @abstractmethod
    async def stop_session(
        self, provider_session_id: str, finished_at: datetime
    ) -> ProviderSessionDTO: ...

    @abstractmethod
    async def extend_session(
        self, provider_session_id: str, duration: timedelta
    ) -> ProviderSessionDTO: ...

    @abstractmethod
    async def get_session(self, provider_session_id: str) -> ProviderSessionDTO: ...

    @abstractmethod
    async def process_payment(self, provider_session_id: str, amount: Decimal) -> str: ...
