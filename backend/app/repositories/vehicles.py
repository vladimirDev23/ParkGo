from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.vehicle import Vehicle


class VehicleRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_for_user(self, user_id: UUID) -> list[Vehicle]:
        result = await self.session.scalars(
            select(Vehicle)
            .where(Vehicle.user_id == user_id)
            .order_by(Vehicle.is_default.desc(), Vehicle.created_at)
        )
        return list(result)

    async def get_for_user(self, vehicle_id: UUID, user_id: UUID) -> Vehicle | None:
        vehicle: Vehicle | None = await self.session.scalar(
            select(Vehicle).where(Vehicle.id == vehicle_id, Vehicle.user_id == user_id)
        )
        return vehicle

    async def clear_default(self, user_id: UUID) -> None:
        await self.session.execute(
            update(Vehicle).where(Vehicle.user_id == user_id).values(is_default=False)
        )

    def add(self, vehicle: Vehicle) -> None:
        self.session.add(vehicle)

    async def delete(self, vehicle: Vehicle) -> None:
        await self.session.delete(vehicle)
