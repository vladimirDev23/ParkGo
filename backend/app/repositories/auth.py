from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.auth import RefreshToken


class RefreshTokenRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_active(self, jti: str, now: datetime) -> RefreshToken | None:
        statement = select(RefreshToken).where(
            RefreshToken.jti == jti,
            RefreshToken.revoked.is_(False),
            RefreshToken.expires_at > now,
        )
        token: RefreshToken | None = await self.session.scalar(statement)
        return token

    def add(self, token: RefreshToken) -> None:
        self.session.add(token)
