from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import SessionStatus
from app.exceptions.domain import VehicleInActiveSessionError, VehicleNotFoundError
from app.models.parking import ParkingSession
from app.models.vehicle import Vehicle
from app.repositories.vehicles import VehicleRepository
from app.schemas.vehicle import VehicleCreate, VehicleUpdate


class VehicleService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.vehicles = VehicleRepository(session)

    async def list(self, user_id: UUID) -> list[Vehicle]:
        return await self.vehicles.list_for_user(user_id)

    async def get(self, vehicle_id: UUID, user_id: UUID) -> Vehicle:
        vehicle = await self.vehicles.get_for_user(vehicle_id, user_id)
        if vehicle is None:
            raise VehicleNotFoundError()
        return vehicle

    async def create(self, user_id: UUID, data: VehicleCreate) -> Vehicle:
        existing = await self.vehicles.list_for_user(user_id)
        should_default = data.is_default or not existing
        if should_default:
            await self.vehicles.clear_default(user_id)
        vehicle = Vehicle(
            user_id=user_id,
            **data.model_dump(exclude={"is_default"}),
            is_default=should_default,
        )
        self.vehicles.add(vehicle)
        await self.session.commit()
        await self.session.refresh(vehicle)
        return vehicle

    async def update(self, vehicle_id: UUID, user_id: UUID, data: VehicleUpdate) -> Vehicle:
        vehicle = await self.get(vehicle_id, user_id)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(vehicle, field, value)
        await self.session.commit()
        await self.session.refresh(vehicle)
        return vehicle

    async def delete(self, vehicle_id: UUID, user_id: UUID) -> None:
        vehicle = await self.get(vehicle_id, user_id)
        active = await self.session.scalar(
            select(ParkingSession.id).where(
                ParkingSession.vehicle_id == vehicle.id,
                ParkingSession.status == SessionStatus.ACTIVE,
            )
        )
        if active:
            raise VehicleInActiveSessionError()
        was_default = vehicle.is_default
        await self.vehicles.delete(vehicle)
        await self.session.flush()
        if was_default:
            remaining = await self.vehicles.list_for_user(user_id)
            if remaining:
                remaining[0].is_default = True
        await self.session.commit()

    async def make_default(self, vehicle_id: UUID, user_id: UUID) -> Vehicle:
        vehicle = await self.get(vehicle_id, user_id)
        await self.vehicles.clear_default(user_id)
        vehicle.is_default = True
        await self.session.commit()
        await self.session.refresh(vehicle)
        return vehicle
