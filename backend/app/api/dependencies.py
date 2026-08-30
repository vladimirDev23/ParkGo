from typing import Annotated

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.db.session import get_db_session
from app.exceptions.domain import AuthenticationError
from app.models.user import User
from app.providers.parking.base import ParkingProvider
from app.providers.parking.factory import get_parking_provider
from app.repositories.users import UserRepository
from app.security.tokens import TokenCodec

DbSession = Annotated[AsyncSession, Depends(get_db_session)]
AppSettings = Annotated[Settings, Depends(get_settings)]
Provider = Annotated[ParkingProvider, Depends(get_parking_provider)]

bearer = HTTPBearer(auto_error=False)


async def get_current_user(
    request: Request,
    session: DbSession,
    settings: AppSettings,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
) -> User:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise AuthenticationError()
    claims = TokenCodec(settings).decode(credentials.credentials, "access")
    user = await UserRepository(session).get(claims.subject)
    if user is None or not user.is_active:
        raise AuthenticationError()
    request.state.user_id = str(user.id)
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
