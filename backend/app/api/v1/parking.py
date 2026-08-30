from uuid import UUID

from fastapi import APIRouter, Query, status

from app.api.dependencies import CurrentUser, DbSession, Provider
from app.schemas.parking import (
    ExtendSessionRequest,
    HistoryResponse,
    NearbyZonesResponse,
    SessionResponse,
    StartSessionRequest,
    StatsResponse,
    ZoneResponse,
)
from app.services.parking import ParkingService

router = APIRouter(prefix="/parking", tags=["Parking"])


@router.get("/nearby", response_model=NearbyZonesResponse)
async def nearby(
    user: CurrentUser,
    session: DbSession,
    provider: Provider,
    latitude: float = Query(ge=-90, le=90),
    longitude: float = Query(ge=-180, le=180),
    radius: int = Query(default=1500, ge=50, le=10_000),
) -> NearbyZonesResponse:
    values = await ParkingService(session, provider).nearby(latitude, longitude, radius)
    return NearbyZonesResponse(
        zones=[ZoneResponse.from_entity(zone, distance) for zone, distance in values]
    )


@router.get("/zones/{zone_id}", response_model=ZoneResponse)
async def get_zone(
    zone_id: UUID, user: CurrentUser, session: DbSession, provider: Provider
) -> ZoneResponse:
    zone = await ParkingService(session, provider).zone(zone_id)
    return ZoneResponse.from_entity(zone)


@router.post("/sessions", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def start_session(
    data: StartSessionRequest, user: CurrentUser, session: DbSession, provider: Provider
) -> SessionResponse:
    value = await ParkingService(session, provider).start(
        user.id, data.vehicle_id, data.parking_zone_id
    )
    return SessionResponse.from_entity(value)


@router.get("/sessions/current", response_model=SessionResponse | None)
async def current_session(
    user: CurrentUser, session: DbSession, provider: Provider
) -> SessionResponse | None:
    value = await ParkingService(session, provider).current(user.id)
    return SessionResponse.from_entity(value) if value else None


@router.get("/sessions/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: UUID, user: CurrentUser, session: DbSession, provider: Provider
) -> SessionResponse:
    value = await ParkingService(session, provider).get(session_id, user.id)
    return SessionResponse.from_entity(value)


@router.post("/sessions/{session_id}/stop", response_model=SessionResponse)
async def stop_session(
    session_id: UUID, user: CurrentUser, session: DbSession, provider: Provider
) -> SessionResponse:
    value = await ParkingService(session, provider).stop(session_id, user.id)
    return SessionResponse.from_entity(value)


@router.post("/sessions/{session_id}/extend", response_model=SessionResponse)
async def extend_session(
    session_id: UUID,
    data: ExtendSessionRequest,
    user: CurrentUser,
    session: DbSession,
    provider: Provider,
) -> SessionResponse:
    value = await ParkingService(session, provider).extend(session_id, user.id, data.minutes)
    return SessionResponse.from_entity(value)


@router.get("/history", response_model=HistoryResponse)
async def history(
    user: CurrentUser,
    session: DbSession,
    provider: Provider,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> HistoryResponse:
    values = await ParkingService(session, provider).history(user.id, limit, offset)
    return HistoryResponse(sessions=[SessionResponse.from_entity(item) for item in values])


@router.get("/stats", response_model=StatsResponse)
async def stats(user: CurrentUser, session: DbSession, provider: Provider) -> StatsResponse:
    return await ParkingService(session, provider).stats(user.id)
