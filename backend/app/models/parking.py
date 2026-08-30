from __future__ import annotations

from datetime import datetime, time
from decimal import Decimal
from typing import TYPE_CHECKING, Any
from uuid import UUID

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Numeric,
    String,
    Text,
    Time,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.type_api import TypeEngine

from app.core.config import get_settings
from app.core.enums import PaymentStatus, SessionStatus
from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.vehicle import Vehicle


def _geometry_column_type() -> TypeEngine[Any]:
    if get_settings().TESTING:
        return Text()
    from geoalchemy2 import Geometry

    return Geometry("POINT", srid=4326, spatial_index=False)


class ParkingZone(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "parking_zones"
    __table_args__ = (
        UniqueConstraint("provider", "external_id", name="uq_zone_provider_external_id"),
        Index("ix_parking_zones_active", "is_active"),
    )

    external_id: Mapped[str] = mapped_column(String(100))
    provider: Mapped[str] = mapped_column(String(50), index=True)
    name: Mapped[str] = mapped_column(String(150))
    zone_number: Mapped[str] = mapped_column(String(30), index=True)
    latitude: Mapped[Decimal] = mapped_column(Numeric(9, 6))
    longitude: Mapped[Decimal] = mapped_column(Numeric(9, 6))
    geometry: Mapped[Any] = mapped_column(_geometry_column_type())
    address: Mapped[str] = mapped_column(String(255))
    hourly_rate: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    currency: Mapped[str] = mapped_column(String(3), default="RUB")
    active_from: Mapped[time | None] = mapped_column(Time())
    active_until: Mapped[time | None] = mapped_column(Time())
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    provider_metadata: Mapped[dict[str, Any]] = mapped_column(
        "metadata", JSON().with_variant(JSONB(), "postgresql"), default=dict
    )

    parking_sessions: Mapped[list[ParkingSession]] = relationship(back_populates="parking_zone")


class ParkingSession(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "parking_sessions"
    __table_args__ = (
        Index("ix_sessions_user_started", "user_id", "started_at"),
        Index(
            "uq_one_active_session_per_user",
            "user_id",
            unique=True,
            postgresql_where=text("status = 'active'"),
            sqlite_where=text("status = 'active'"),
        ),
    )

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    vehicle_id: Mapped[UUID] = mapped_column(ForeignKey("vehicles.id"), index=True)
    parking_zone_id: Mapped[UUID] = mapped_column(ForeignKey("parking_zones.id"), index=True)
    provider_session_id: Mapped[str | None] = mapped_column(String(150), unique=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[SessionStatus] = mapped_column(
        Enum(
            SessionStatus,
            native_enum=False,
            values_callable=lambda enum: [e.value for e in enum],
        ),
        default=SessionStatus.ACTIVE,
        index=True,
    )
    calculated_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0"))
    paid_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0"))
    currency: Mapped[str] = mapped_column(String(3), default="RUB")
    payment_status: Mapped[PaymentStatus] = mapped_column(
        Enum(
            PaymentStatus,
            native_enum=False,
            values_callable=lambda enum: [e.value for e in enum],
        ),
        default=PaymentStatus.PENDING,
    )

    user: Mapped[User] = relationship(back_populates="parking_sessions")
    vehicle: Mapped[Vehicle] = relationship(back_populates="parking_sessions")
    parking_zone: Mapped[ParkingZone] = relationship(back_populates="parking_sessions")
    payment: Mapped[Payment | None] = relationship(back_populates="session", uselist=False)


class Payment(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "payments"

    session_id: Mapped[UUID] = mapped_column(
        ForeignKey("parking_sessions.id"), unique=True, index=True
    )
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    provider: Mapped[str] = mapped_column(String(50))
    external_payment_id: Mapped[str] = mapped_column(String(150), unique=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    status: Mapped[PaymentStatus] = mapped_column(
        Enum(PaymentStatus, native_enum=False, values_callable=lambda enum: [e.value for e in enum])
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    session: Mapped[ParkingSession] = relationship(back_populates="payment")
