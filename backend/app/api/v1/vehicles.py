from uuid import UUID

from fastapi import APIRouter, Response, status

from app.api.dependencies import CurrentUser, DbSession
from app.schemas.vehicle import VehicleCreate, VehicleResponse, VehicleUpdate
from app.services.vehicles import VehicleService

router = APIRouter(prefix="/vehicles", tags=["Vehicles"])


@router.get("", response_model=list[VehicleResponse])
async def list_vehicles(user: CurrentUser, session: DbSession) -> list[VehicleResponse]:
    vehicles = await VehicleService(session).list(user.id)
    return [VehicleResponse.model_validate(vehicle) for vehicle in vehicles]


@router.post("", response_model=VehicleResponse, status_code=status.HTTP_201_CREATED)
async def create_vehicle(
    data: VehicleCreate, user: CurrentUser, session: DbSession
) -> VehicleResponse:
    vehicle = await VehicleService(session).create(user.id, data)
    return VehicleResponse.model_validate(vehicle)


@router.get("/{vehicle_id}", response_model=VehicleResponse)
async def get_vehicle(vehicle_id: UUID, user: CurrentUser, session: DbSession) -> VehicleResponse:
    vehicle = await VehicleService(session).get(vehicle_id, user.id)
    return VehicleResponse.model_validate(vehicle)


@router.patch("/{vehicle_id}", response_model=VehicleResponse)
async def update_vehicle(
    vehicle_id: UUID, data: VehicleUpdate, user: CurrentUser, session: DbSession
) -> VehicleResponse:
    vehicle = await VehicleService(session).update(vehicle_id, user.id, data)
    return VehicleResponse.model_validate(vehicle)


@router.delete("/{vehicle_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vehicle(vehicle_id: UUID, user: CurrentUser, session: DbSession) -> Response:
    await VehicleService(session).delete(vehicle_id, user.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{vehicle_id}/default", response_model=VehicleResponse)
async def default_vehicle(
    vehicle_id: UUID, user: CurrentUser, session: DbSession
) -> VehicleResponse:
    vehicle = await VehicleService(session).make_default(vehicle_id, user.id)
    return VehicleResponse.model_validate(vehicle)
