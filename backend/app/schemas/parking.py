from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_serializer

from app.core.enums import PaymentStatus, SessionStatus
from app.models.parking import ParkingSession, ParkingZone
from app.schemas.vehicle import VehicleResponse


class ZoneResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    zone_number: str
    name: str
    address: str
    latitude: Decimal
    longitude: Decimal
    distance_meters: int | None = None
    hourly_rate: Decimal
    currency: str
    active_from: str | None = None
    active_until: str | None = None
    is_active: bool

    @field_serializer("latitude", "longitude", when_used="json")
    def serialize_coordinate(self, value: Decimal) -> float:
        return float(value)

    @field_serializer("hourly_rate", when_used="json")
    def serialize_rate(self, value: Decimal) -> str:
        return f"{value:.2f}"

    @classmethod
    def from_entity(cls, zone: ParkingZone, distance_meters: int | None = None) -> ZoneResponse:
        return cls(
            id=zone.id,
            zone_number=zone.zone_number,
            name=zone.name,
            address=zone.address,
            latitude=zone.latitude,
            longitude=zone.longitude,
            distance_meters=distance_meters,
            hourly_rate=zone.hourly_rate,
            currency=zone.currency,
            active_from=(
                zone.active_from.isoformat(timespec="minutes") if zone.active_from else None
            ),
            active_until=(
                zone.active_until.isoformat(timespec="minutes") if zone.active_until else None
            ),
            is_active=zone.is_active,
        )


class NearbyZonesResponse(BaseModel):
    zones: list[ZoneResponse]


class StartSessionRequest(BaseModel):
    vehicle_id: UUID
    parking_zone_id: UUID


class ExtendSessionRequest(BaseModel):
    minutes: int = Field(ge=1, le=1440)


class SessionResponse(BaseModel):
    id: UUID
    started_at: datetime
    finished_at: datetime | None
    status: SessionStatus
    calculated_amount: Decimal
    paid_amount: Decimal
    currency: str
    payment_status: PaymentStatus
    vehicle: VehicleResponse
    parking_zone: ZoneResponse

    @field_serializer("calculated_amount", "paid_amount", when_used="json")
    def serialize_amount(self, value: Decimal) -> str:
        return f"{value:.2f}"

    @classmethod
    def from_entity(cls, entity: ParkingSession) -> SessionResponse:
        return cls(
            id=entity.id,
            started_at=entity.started_at,
            finished_at=entity.finished_at,
            status=entity.status,
            calculated_amount=entity.calculated_amount,
            paid_amount=entity.paid_amount,
            currency=entity.currency,
            payment_status=entity.payment_status,
            vehicle=VehicleResponse.model_validate(entity.vehicle),
            parking_zone=ZoneResponse.from_entity(entity.parking_zone),
        )


class HistoryResponse(BaseModel):
    sessions: list[SessionResponse]


class StatsResponse(BaseModel):
    period: str
    parking_count: int
    total_duration_seconds: int
    total_spent: Decimal
    average_amount: Decimal
    most_used_zone_number: str | None

    @field_serializer("total_spent", "average_amount", when_used="json")
    def serialize_amount(self, value: Decimal) -> str:
        return f"{value:.2f}"
