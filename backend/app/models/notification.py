from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, Enum, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import DevicePlatform
from app.db.base import Base, UUIDPrimaryKeyMixin


class NotificationDevice(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "notification_devices"
    __table_args__ = (
        UniqueConstraint("platform", "push_token", name="uq_notification_platform_token"),
    )

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    platform: Mapped[DevicePlatform] = mapped_column(
        Enum(
            DevicePlatform,
            native_enum=False,
            values_callable=lambda enum: [e.value for e in enum],
        )
    )
    push_token: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
