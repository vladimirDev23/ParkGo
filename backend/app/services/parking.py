from collections import Counter
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import PaymentStatus, SessionStatus
from app.exceptions.domain import (
    InvalidZoneError,
    ParkingSessionNotFoundError,
    ParkingZoneNotFoundError,
    PaymentFailedError,
    SessionAlreadyActiveError,
    VehicleNotFoundError,
)
from app.models.parking import ParkingSession, ParkingZone, Payment
from app.providers.parking.base import ParkingProvider
from app.repositories.parking import ParkingSessionRepository, ZoneRepository
from app.repositories.vehicles import VehicleRepository
from app.schemas.parking import StatsResponse


class ParkingService:
    def __init__(self, session: AsyncSession, provider: ParkingProvider) -> None:
        self.session = session
        self.provider = provider
        self.zones = ZoneRepository(session)
        self.sessions = ParkingSessionRepository(session)
        self.vehicles = VehicleRepository(session)

    async def nearby(
        self, latitude: float, longitude: float, radius: int
    ) -> list[tuple[ParkingZone, int]]:
        provider_zones = await self.provider.get_nearby_zones(latitude, longitude, radius)
        await self.zones.sync(provider_zones)
        await self.session.commit()
        return await self.zones.nearby(latitude, longitude, radius)

    async def zone(self, zone_id: UUID) -> ParkingZone:
        zone = await self.zones.get(zone_id)
        if zone is None:
            raise ParkingZoneNotFoundError()
        return zone

    async def start(self, user_id: UUID, vehicle_id: UUID, zone_id: UUID) -> ParkingSession:
        if await self.sessions.current(user_id, lock=True):
            raise SessionAlreadyActiveError()
        vehicle = await self.vehicles.get_for_user(vehicle_id, user_id)
        if vehicle is None:
            raise VehicleNotFoundError()
        zone = await self.zones.get(zone_id)
        if zone is None:
            raise ParkingZoneNotFoundError()
        if not zone.is_active:
            raise InvalidZoneError()
        await self.provider.get_zone(zone.external_id)
        now = datetime.now(UTC)
        provider_session = await self.provider.start_session(
            zone.external_id, f"{vehicle.plate_number} {vehicle.region_code}".strip(), now
        )
        parking_session = ParkingSession(
            user_id=user_id,
            vehicle_id=vehicle.id,
            parking_zone_id=zone.id,
            provider_session_id=provider_session.id,
            started_at=provider_session.started_at,
            status=SessionStatus.ACTIVE,
            calculated_amount=Decimal("0.00"),
            paid_amount=Decimal("0.00"),
            currency=provider_session.price.currency,
            payment_status=PaymentStatus.PENDING,
        )
        self.sessions.add(parking_session)
        try:
            await self.session.commit()
        except IntegrityError as exc:
            await self.session.rollback()
            try:
                await self.provider.stop_session(provider_session.id, datetime.now(UTC))
            finally:
                raise SessionAlreadyActiveError() from exc
        result = await self.sessions.get_for_user(parking_session.id, user_id)
        assert result is not None
        return result

    async def current(self, user_id: UUID) -> ParkingSession | None:
        return await self.sessions.current(user_id)

    async def get(self, session_id: UUID, user_id: UUID) -> ParkingSession:
        parking_session = await self.sessions.get_for_user(session_id, user_id)
        if parking_session is None:
            raise ParkingSessionNotFoundError()
        return parking_session

    async def stop(self, session_id: UUID, user_id: UUID) -> ParkingSession:
        parking_session = await self.sessions.get_for_user(session_id, user_id, lock=True)
        if parking_session is None or parking_session.status != SessionStatus.ACTIVE:
            raise ParkingSessionNotFoundError()
        if parking_session.provider_session_id is None:
            raise ParkingSessionNotFoundError()

        finished_at = datetime.now(UTC)
        price = await self.provider.calculate_price(
            parking_session.parking_zone.external_id,
            f"{parking_session.vehicle.plate_number} {parking_session.vehicle.region_code}".strip(),
            parking_session.started_at,
            finished_at,
        )
        await self.provider.stop_session(parking_session.provider_session_id, finished_at)
        parking_session.finished_at = finished_at
        parking_session.status = SessionStatus.COMPLETED
        parking_session.calculated_amount = price.amount

        try:
            external_payment_id = await self.provider.process_payment(
                parking_session.provider_session_id, price.amount
            )
            payment_status = PaymentStatus.PAID
            parking_session.paid_amount = price.amount
            parking_session.payment_status = PaymentStatus.PAID
        except PaymentFailedError:
            external_payment_id = f"failed-{parking_session.id}"
            payment_status = PaymentStatus.FAILED
            parking_session.paid_amount = Decimal("0.00")
            parking_session.payment_status = PaymentStatus.FAILED

        self.session.add(
            Payment(
                session_id=parking_session.id,
                user_id=user_id,
                provider=self.provider.name,
                external_payment_id=external_payment_id,
                amount=price.amount,
                status=payment_status,
                created_at=finished_at,
            )
        )
        await self.session.commit()
        result = await self.sessions.get_for_user(parking_session.id, user_id)
        assert result is not None
        if payment_status == PaymentStatus.FAILED:
            raise PaymentFailedError(details={"session_id": str(parking_session.id)})
        return result

    async def extend(self, session_id: UUID, user_id: UUID, minutes: int) -> ParkingSession:
        parking_session = await self.sessions.get_for_user(session_id, user_id)
        if parking_session is None or parking_session.status != SessionStatus.ACTIVE:
            raise ParkingSessionNotFoundError()
        if parking_session.provider_session_id is None:
            raise ParkingSessionNotFoundError()
        await self.provider.extend_session(
            parking_session.provider_session_id, timedelta(minutes=minutes)
        )
        return parking_session

    async def history(self, user_id: UUID, limit: int, offset: int) -> list[ParkingSession]:
        return await self.sessions.history(user_id, limit=limit, offset=offset)

    async def stats(self, user_id: UUID, now: datetime | None = None) -> StatsResponse:
        moment = now or datetime.now(UTC)
        start = datetime(moment.year, moment.month, 1, tzinfo=UTC)
        end = datetime(moment.year + (moment.month == 12), (moment.month % 12) + 1, 1, tzinfo=UTC)
        sessions = await self.sessions.completed_between(user_id, start, end)
        total = sum((item.paid_amount for item in sessions), Decimal("0.00"))
        duration = sum(
            max(0, int(((item.finished_at or item.started_at) - item.started_at).total_seconds()))
            for item in sessions
        )
        zone_counts = Counter(item.parking_zone.zone_number for item in sessions)
        most_used = zone_counts.most_common(1)[0][0] if zone_counts else None
        average = (total / len(sessions)).quantize(Decimal("0.01")) if sessions else Decimal("0.00")
        return StatsResponse(
            period=start.strftime("%Y-%m"),
            parking_count=len(sessions),
            total_duration_seconds=duration,
            total_spent=total,
            average_amount=average,
            most_used_zone_number=most_used,
        )
