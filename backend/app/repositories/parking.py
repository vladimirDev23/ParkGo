from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import cast, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import get_settings
from app.core.enums import SessionStatus
from app.models.parking import ParkingSession, ParkingZone
from app.providers.parking.dto import ParkingZoneDTO
from app.providers.parking.mock import haversine_meters


class ZoneRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, zone_id: UUID) -> ParkingZone | None:
        return await self.session.get(ParkingZone, zone_id)

    async def get_by_external(self, provider: str, external_id: str) -> ParkingZone | None:
        zone: ParkingZone | None = await self.session.scalar(
            select(ParkingZone).where(
                ParkingZone.provider == provider,
                ParkingZone.external_id == external_id,
            )
        )
        return zone

    async def sync(self, zones: list[ParkingZoneDTO]) -> None:
        for dto in zones:
            zone = await self.get_by_external(dto.provider, dto.external_id)
            values = {
                "name": dto.name,
                "zone_number": dto.zone_number,
                "latitude": Decimal(str(dto.latitude)),
                "longitude": Decimal(str(dto.longitude)),
                "geometry": f"SRID=4326;POINT({dto.longitude} {dto.latitude})",
                "address": dto.address,
                "hourly_rate": dto.hourly_rate,
                "currency": dto.currency,
                "active_from": dto.active_from,
                "active_until": dto.active_until,
                "is_active": dto.is_active,
                "provider_metadata": dto.metadata,
            }
            if zone is None:
                self.session.add(
                    ParkingZone(provider=dto.provider, external_id=dto.external_id, **values)
                )
            else:
                for key, value in values.items():
                    setattr(zone, key, value)
        await self.session.flush()

    async def nearby(
        self, latitude: float, longitude: float, radius_meters: int
    ) -> list[tuple[ParkingZone, int]]:
        is_postgres = (
            self.session.bind is not None and self.session.bind.dialect.name == "postgresql"
        )
        if get_settings().TESTING or not is_postgres:
            zones = list(
                await self.session.scalars(
                    select(ParkingZone).where(ParkingZone.is_active.is_(True))
                )
            )
            with_distance = [
                (
                    zone,
                    round(
                        haversine_meters(
                            latitude,
                            longitude,
                            float(zone.latitude),
                            float(zone.longitude),
                        )
                    ),
                )
                for zone in zones
            ]
            return sorted(
                (item for item in with_distance if item[1] <= radius_meters),
                key=lambda item: item[1],
            )

        from geoalchemy2 import Geography

        point = func.ST_SetSRID(func.ST_MakePoint(longitude, latitude), 4326)
        zone_geography = cast(ParkingZone.geometry, Geography(geometry_type="POINT", srid=4326))
        point_geography = cast(point, Geography(geometry_type="POINT", srid=4326))
        distance = func.ST_Distance(zone_geography, point_geography)
        rows = await self.session.execute(
            select(ParkingZone, distance.label("distance"))
            .where(
                ParkingZone.is_active.is_(True),
                func.ST_DWithin(zone_geography, point_geography, radius_meters),
            )
            .order_by(distance)
        )
        return [(zone, round(float(meters))) for zone, meters in rows]


class ParkingSessionRepository:
    load_options = (
        selectinload(ParkingSession.vehicle),
        selectinload(ParkingSession.parking_zone),
        selectinload(ParkingSession.payment),
    )

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def current(self, user_id: UUID, *, lock: bool = False) -> ParkingSession | None:
        statement = (
            select(ParkingSession)
            .options(*self.load_options)
            .where(
                ParkingSession.user_id == user_id,
                ParkingSession.status == SessionStatus.ACTIVE,
            )
        )
        if lock:
            statement = statement.with_for_update()
        parking_session: ParkingSession | None = await self.session.scalar(statement)
        return parking_session

    async def get_for_user(
        self, session_id: UUID, user_id: UUID, *, lock: bool = False
    ) -> ParkingSession | None:
        statement = (
            select(ParkingSession)
            .options(*self.load_options)
            .where(ParkingSession.id == session_id, ParkingSession.user_id == user_id)
        )
        if lock:
            statement = statement.with_for_update()
        parking_session: ParkingSession | None = await self.session.scalar(statement)
        return parking_session

    async def history(self, user_id: UUID, *, limit: int, offset: int) -> list[ParkingSession]:
        values = await self.session.scalars(
            select(ParkingSession)
            .options(*self.load_options)
            .where(
                ParkingSession.user_id == user_id,
                ParkingSession.status != SessionStatus.ACTIVE,
            )
            .order_by(ParkingSession.started_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(values)

    async def completed_between(
        self, user_id: UUID, start: datetime, end: datetime
    ) -> list[ParkingSession]:
        values = await self.session.scalars(
            select(ParkingSession)
            .options(*self.load_options)
            .where(
                ParkingSession.user_id == user_id,
                ParkingSession.status == SessionStatus.COMPLETED,
                ParkingSession.started_at >= start,
                ParkingSession.started_at < end,
            )
        )
        return list(values)

    def add(self, parking_session: ParkingSession) -> None:
        self.session.add(parking_session)
