from fastapi import APIRouter, Request, status

from app.api.dependencies import AppSettings, CurrentUser, DbSession
from app.schemas.auth import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenPairResponse,
    UserResponse,
)
from app.security.rate_limit import AuthRateLimiter
from app.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])
_rate_limiters: dict[str, AuthRateLimiter] = {}


def get_limiter(settings: AppSettings) -> AuthRateLimiter:
    key = settings.REDIS_URL
    if key not in _rate_limiters:
        _rate_limiters[key] = AuthRateLimiter(settings)
    return _rate_limiters[key]


def request_key(request: Request, email: str = "") -> str:
    host = request.client.host if request.client else "unknown"
    return f"{host}:{email.lower()}"


@router.post("/register", response_model=TokenPairResponse, status_code=status.HTTP_201_CREATED)
async def register(
    data: RegisterRequest, request: Request, session: DbSession, settings: AppSettings
) -> TokenPairResponse:
    await get_limiter(settings).check(request_key(request, data.email))
    return await AuthService(session, settings).register(data)


@router.post("/login", response_model=TokenPairResponse)
async def login(
    data: LoginRequest, request: Request, session: DbSession, settings: AppSettings
) -> TokenPairResponse:
    await get_limiter(settings).check(request_key(request, data.email))
    return await AuthService(session, settings).login(data)


@router.post("/refresh", response_model=TokenPairResponse)
async def refresh(
    data: RefreshRequest, request: Request, session: DbSession, settings: AppSettings
) -> TokenPairResponse:
    await get_limiter(settings).check(request_key(request, "refresh"))
    return await AuthService(session, settings).refresh(data.refresh_token)


@router.get("/me", response_model=UserResponse)
async def me(user: CurrentUser) -> UserResponse:
    return UserResponse.model_validate(user)
