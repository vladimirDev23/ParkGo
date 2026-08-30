import asyncio
import math
from datetime import UTC, datetime, time, timedelta
from decimal import ROUND_CEILING, Decimal
from enum import StrEnum
from uuid import uuid4

from app.core.enums import SessionStatus
from app.exceptions.domain import (
    InvalidZoneError,
    PaymentFailedError,
    ProviderUnavailableError,
    SessionAlreadyActiveError,
    VehicleNotAllowedError,
)
from app.providers.parking.base import ParkingProvider
from app.providers.parking.dto import ParkingZoneDTO, PriceDTO, ProviderSessionDTO


class MockFailure(StrEnum):
    NONE = "none"
    UNAVAILABLE = "unavailable"
    PAYMENT_FAILED = "payment_failed"
    VEHICLE_NOT_ALLOWED = "vehicle_not_allowed"


ZONE_FIXTURES: tuple[ParkingZoneDTO, ...] = (
    ParkingZoneDTO(
        "demo-1001",
        "mock",
        "Красная / Северная",
        "1001",
        45.0356,
        38.9754,
        "ул. Красная, 122",
        Decimal("60.00"),
        active_from=time(8),
        active_until=time(20),
    ),
    ParkingZoneDTO(
        "demo-1002",
        "mock",
        "Красная / Головатого",
        "1002",
        45.0391,
        38.9748,
        "ул. Красная, 145",
        Decimal("60.00"),
        active_from=time(8),
        active_until=time(20),
    ),
    ParkingZoneDTO(
        "demo-1003",
        "mock",
        "Театральная площадь",
        "1003",
        45.0330,
        38.9747,
        "Театральная площадь",
        Decimal("70.00"),
        active_from=time(8),
        active_until=time(22),
    ),
    ParkingZoneDTO(
        "demo-1004",
        "mock",
        "Красная / Мира",
        "1004",
        45.0279,
        38.9686,
        "ул. Красная, 55",
        Decimal("60.00"),
        active_from=time(8),
        active_until=time(20),
    ),
    ParkingZoneDTO(
        "demo-1005",
        "mock",
        "Кооперативный рынок",
        "1005",
        45.0306,
        38.9698,
        "ул. Карасунская, 86",
        Decimal("50.00"),
        active_from=time(8),
        active_until=time(20),
    ),
    ParkingZoneDTO(
        "demo-1006",
        "mock",
        "Городской сад",
        "1006",
        45.0245,
        38.9682,
        "ул. Постовая, 34",
        Decimal("50.00"),
        active_from=time(8),
        active_until=time(20),
    ),
    ParkingZoneDTO(
        "demo-1007",
        "mock",
        "Чистяковская роща",
        "1007",
        45.0505,
        39.0282,
        "ул. Колхозная, 86",
        Decimal("40.00"),
        active_from=time(8),
        active_until=time(20),
    ),
    ParkingZoneDTO(
        "demo-1008",
        "mock",
        "Аврора",
        "1008",
        45.0546,
        38.9772,
        "ул. Красная, 169",
        Decimal("60.00"),
        active_from=time(8),
        active_until=time(22),
    ),
    ParkingZoneDTO(
        "demo-1009",
        "mock",
        "Железнодорожный вокзал",
        "1009",
        45.0187,
        38.9869,
        "Привокзальная площадь, 1",
        Decimal("80.00"),
        active_from=time(0),
        active_until=time(23, 59),
    ),
    ParkingZoneDTO(
        "demo-1010",
        "mock",
        "Кубанская набережная",
        "1010",
        45.0232,
        38.9566,
        "ул. Кубанская Набережная, 39",
        Decimal("50.00"),
        active_from=time(8),
        active_until=time(22),
    ),
    ParkingZoneDTO(
        "demo-1011",
        "mock",
        "Сенной рынок",
        "1011",
        45.0417,
        38.9670,
        "ул. Длинная, 120",
        Decimal("60.00"),
        active_from=time(8),
        active_until=time(20),
    ),
    ParkingZoneDTO(
        "demo-1012",
        "mock",
        "Галерея Краснодар",
        "1012",
        45.0397,
        38.9731,
        "ул. Володи Головатого, 313",
        Decimal("80.00"),
        active_from=time(8),
        active_until=time(23),
    ),
    ParkingZoneDTO(
        "demo-1013",
        "mock",
        "Стадион Кубань",
        "1013",
        45.0218,
        39.0010,
        "ул. Железнодорожная, 49",
        Decimal("50.00"),
        active_from=time(8),
        active_until=time(22),
    ),
    ParkingZoneDTO(
        "demo-1014",
        "mock",
        "Зиповская",
        "1014",
        45.0648,
        39.0044,
        "ул. Зиповская, 5",
        Decimal("40.00"),
        active_from=time(8),
        active_until=time(20),
    ),
    ParkingZoneDTO(
        "demo-1015",
        "mock",
        "Улица Рашпилевская",
        "1015",
        45.0370,
        38.9710,
        "ул. Рашпилевская, 110",
        Decimal("60.00"),
        active_from=time(8),
        active_until=time(20),
    ),
)


def haversine_meters(
    latitude_a: float, longitude_a: float, latitude_b: float, longitude_b: float
) -> float:
    earth_radius = 6_371_000.0
    phi_a, phi_b = math.radians(latitude_a), math.radians(latitude_b)
    delta_phi = math.radians(latitude_b - latitude_a)
    delta_lambda = math.radians(longitude_b - longitude_a)
    value = (
        math.sin(delta_phi / 2) ** 2
        + math.cos(phi_a) * math.cos(phi_b) * math.sin(delta_lambda / 2) ** 2
    )
    return earth_radius * 2 * math.atan2(math.sqrt(value), math.sqrt(1 - value))


def as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


class MockParkingProvider(ParkingProvider):
    name = "mock"

    def __init__(self, *, latency_seconds: float = 0.01) -> None:
        self.latency_seconds = latency_seconds
        self.failure = MockFailure.NONE
        self._sessions: dict[str, ProviderSessionDTO] = {}

    async def _prepare(self) -> None:
        if self.latency_seconds:
            await asyncio.sleep(self.latency_seconds)
        if self.failure == MockFailure.UNAVAILABLE:
            raise ProviderUnavailableError()

    async def get_nearby_zones(
        self, latitude: float, longitude: float, radius_meters: int
    ) -> list[ParkingZoneDTO]:
        await self._prepare()
        found: list[ParkingZoneDTO] = []
        for zone in ZONE_FIXTURES:
            distance = round(haversine_meters(latitude, longitude, zone.latitude, zone.longitude))
            if distance <= radius_meters:
                found.append(
                    ParkingZoneDTO(
                        external_id=zone.external_id,
                        provider=zone.provider,
                        name=zone.name,
                        zone_number=zone.zone_number,
                        latitude=zone.latitude,
                        longitude=zone.longitude,
                        address=zone.address,
                        hourly_rate=zone.hourly_rate,
                        currency=zone.currency,
                        active_from=zone.active_from,
                        active_until=zone.active_until,
                        is_active=zone.is_active,
                        distance_meters=distance,
                        metadata=zone.metadata,
                    )
                )
        return sorted(found, key=lambda zone: zone.distance_meters or 0)

    async def get_zone(self, external_zone_id: str) -> ParkingZoneDTO:
        await self._prepare()
        zone = next((item for item in ZONE_FIXTURES if item.external_id == external_zone_id), None)
        if zone is None or not zone.is_active:
            raise InvalidZoneError()
        return zone

    async def calculate_price(
        self,
        zone_id: str,
        vehicle_plate: str,
        started_at: datetime,
        finished_at: datetime,
    ) -> PriceDTO:
        zone = await self.get_zone(zone_id)
        started_at = as_utc(started_at)
        finished_at = as_utc(finished_at)
        if finished_at < started_at:
            raise InvalidZoneError("Parking finish time cannot precede its start time.")
        seconds = Decimal(str((finished_at - started_at).total_seconds()))
        started_minutes = (seconds / Decimal(60)).quantize(Decimal("1"), rounding=ROUND_CEILING)
        amount = (zone.hourly_rate * max(started_minutes, Decimal(1)) / Decimal(60)).quantize(
            Decimal("0.01")
        )
        return PriceDTO(amount, zone.currency, datetime.now(UTC))

    async def start_session(
        self, zone_id: str, vehicle_plate: str, started_at: datetime
    ) -> ProviderSessionDTO:
        await self._prepare()
        await self.get_zone(zone_id)
        if self.failure == MockFailure.VEHICLE_NOT_ALLOWED or vehicle_plate.startswith("ERROR"):
            raise VehicleNotAllowedError()
        if any(
            item.vehicle_plate == vehicle_plate and item.status == SessionStatus.ACTIVE
            for item in self._sessions.values()
        ):
            raise SessionAlreadyActiveError()
        session_id = f"mock-session-{uuid4()}"
        session = ProviderSessionDTO(
            id=session_id,
            zone_id=zone_id,
            vehicle_plate=vehicle_plate,
            started_at=started_at,
            finished_at=None,
            status=SessionStatus.ACTIVE,
            price=PriceDTO(Decimal("0.00"), "RUB", started_at),
        )
        self._sessions[session_id] = session
        return session

    async def stop_session(
        self, provider_session_id: str, finished_at: datetime
    ) -> ProviderSessionDTO:
        await self._prepare()
        session = await self.get_session(provider_session_id)
        price = await self.calculate_price(
            session.zone_id, session.vehicle_plate, session.started_at, finished_at
        )
        completed = ProviderSessionDTO(
            id=session.id,
            zone_id=session.zone_id,
            vehicle_plate=session.vehicle_plate,
            started_at=session.started_at,
            finished_at=finished_at,
            status=SessionStatus.COMPLETED,
            price=price,
        )
        self._sessions[provider_session_id] = completed
        return completed

    async def extend_session(
        self, provider_session_id: str, duration: timedelta
    ) -> ProviderSessionDTO:
        await self._prepare()
        if duration <= timedelta(0):
            raise InvalidZoneError("Extension duration must be positive.")
        return await self.get_session(provider_session_id)

    async def get_session(self, provider_session_id: str) -> ProviderSessionDTO:
        await self._prepare()
        try:
            return self._sessions[provider_session_id]
        except KeyError as exc:
            raise InvalidZoneError("Provider session was not found.") from exc

    async def process_payment(self, provider_session_id: str, amount: Decimal) -> str:
        await self._prepare()
        await self.get_session(provider_session_id)
        if self.failure == MockFailure.PAYMENT_FAILED:
            raise PaymentFailedError()
        return f"mock-payment-{uuid4()}"
