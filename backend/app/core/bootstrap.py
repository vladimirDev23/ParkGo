from datetime import UTC, datetime, timedelta
from decimal import Decimal

from sqlalchemy import select

from app.core.config import Settings
from app.core.enums import PaymentStatus, SessionStatus
from app.db.session import SessionFactory
from app.models.parking import ParkingSession, ParkingZone, Payment
from app.models.user import User
from app.models.vehicle import Vehicle
from app.providers.parking.mock import ZONE_FIXTURES
from app.repositories.parking import ZoneRepository
from app.security.passwords import hash_password


async def seed_demo_data(settings: Settings) -> None:
    if settings.PARKING_PROVIDER != "mock":
        return
    async with SessionFactory() as session:
        zones = ZoneRepository(session)
        await zones.sync(list(ZONE_FIXTURES))
        if settings.PRESENTATION_MODE:
            user = await session.scalar(select(User).where(User.email == "demo@parkgo.local"))
            if user is None:
                user = User(
                    email="demo@parkgo.local",
                    password_hash=hash_password("DemoPass123!"),
                    first_name="Алексей",
                    is_active=True,
                )
                session.add(user)
                await session.flush()
            vehicle = await session.scalar(
                select(Vehicle).where(Vehicle.user_id == user.id, Vehicle.is_default.is_(True))
            )
            if vehicle is None:
                vehicle = Vehicle(
                    user_id=user.id,
                    plate_number="А123АА",
                    region_code="23",
                    display_name="Toyota RAV4",
                    brand="Toyota",
                    model="RAV4",
                    color="Белый",
                    is_default=True,
                )
                session.add(vehicle)
                await session.flush()
            history_exists = await session.scalar(
                select(ParkingSession.id).where(
                    ParkingSession.user_id == user.id,
                    ParkingSession.status == SessionStatus.COMPLETED,
                )
            )
            if history_exists is None:
                zone_rows = list(await session.scalars(select(ParkingZone).limit(3)))
                now = datetime.now(UTC)
                for index, zone in enumerate(zone_rows):
                    started = now - timedelta(days=index + 1, hours=2)
                    finished = started + timedelta(minutes=65 + index * 11)
                    amount = Decimal(str(70 + index * 12)).quantize(Decimal("0.00"))
                    parking = ParkingSession(
                        user_id=user.id,
                        vehicle_id=vehicle.id,
                        parking_zone_id=zone.id,
                        provider_session_id=f"presentation-history-{index}",
                        started_at=started,
                        finished_at=finished,
                        status=SessionStatus.COMPLETED,
                        calculated_amount=amount,
                        paid_amount=amount,
                        currency="RUB",
                        payment_status=PaymentStatus.PAID,
                    )
                    session.add(parking)
                    await session.flush()
                    session.add(
                        Payment(
                            session_id=parking.id,
                            user_id=user.id,
                            provider="mock",
                            external_payment_id=f"presentation-payment-{index}",
                            amount=amount,
                            status=PaymentStatus.PAID,
                            created_at=finished,
                        )
                    )
        await session.commit()
