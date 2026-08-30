from dataclasses import dataclass, field
from datetime import datetime, time
from decimal import Decimal
from typing import Any

from app.core.enums import SessionStatus


@dataclass(frozen=True, slots=True)
class ParkingZoneDTO:
    external_id: str
    provider: str
    name: str
    zone_number: str
    latitude: float
    longitude: float
    address: str
    hourly_rate: Decimal
    currency: str = "RUB"
    active_from: time | None = None
    active_until: time | None = None
    is_active: bool = True
    distance_meters: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class PriceDTO:
    amount: Decimal
    currency: str
    calculated_at: datetime


@dataclass(frozen=True, slots=True)
class ProviderSessionDTO:
    id: str
    zone_id: str
    vehicle_plate: str
    started_at: datetime
    finished_at: datetime | None
    status: SessionStatus
    price: PriceDTO
