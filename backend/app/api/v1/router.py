from fastapi import APIRouter

from app.api.v1 import auth, health, parking, vehicles

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(vehicles.router)
api_router.include_router(parking.router)
api_router.include_router(health.router)
