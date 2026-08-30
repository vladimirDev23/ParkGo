from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import column

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.parking import ParkingSession
    from app.models.user import User


class Vehicle(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "vehicles"
    __table_args__ = (
        UniqueConstraint("user_id", "plate_number", "region_code", name="uq_vehicle_plate"),
        Index(
            "uq_vehicle_one_default_per_user",
            "user_id",
            unique=True,
            postgresql_where=column("is_default").is_(True),
            sqlite_where=column("is_default").is_(True),
        ),
    )

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    plate_number: Mapped[str] = mapped_column(String(20))
    region_code: Mapped[str] = mapped_column(String(10), default="")
    display_name: Mapped[str] = mapped_column(String(100))
    brand: Mapped[str | None] = mapped_column(String(80))
    model: Mapped[str | None] = mapped_column(String(80))
    color: Mapped[str | None] = mapped_column(String(50))
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    user: Mapped[User] = relationship(back_populates="vehicles")
    parking_sessions: Mapped[list[ParkingSession]] = relationship(back_populates="vehicle")
