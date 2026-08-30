from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.exceptions.domain import (
    AuthenticationError,
    EmailAlreadyRegisteredError,
    InvalidCredentialsError,
)
from app.models.auth import RefreshToken
from app.models.user import User
from app.repositories.auth import RefreshTokenRepository
from app.repositories.users import UserRepository
from app.schemas.auth import LoginRequest, RegisterRequest, TokenPairResponse, UserResponse
from app.security.passwords import hash_password, run_dummy_verify, verify_password
from app.security.tokens import TokenCodec, token_digest


class AuthService:
    def __init__(self, session: AsyncSession, settings: Settings) -> None:
        self.session = session
        self.settings = settings
        self.users = UserRepository(session)
        self.refresh_tokens = RefreshTokenRepository(session)
        self.codec = TokenCodec(settings)

    async def register(self, data: RegisterRequest) -> TokenPairResponse:
        email = data.email.lower()
        if await self.users.get_by_email(email):
            raise EmailAlreadyRegisteredError()
        user = User(
            email=email,
            password_hash=hash_password(data.password),
            first_name=data.first_name,
            is_active=True,
        )
        self.users.add(user)
        await self.session.flush()
        response = await self._issue_pair(user)
        await self.session.commit()
        return response

    async def login(self, data: LoginRequest) -> TokenPairResponse:
        user = await self.users.get_by_email(data.email.lower())
        if user is None:
            run_dummy_verify(data.password)
            raise InvalidCredentialsError()
        if not verify_password(data.password, user.password_hash) or not user.is_active:
            raise InvalidCredentialsError()
        response = await self._issue_pair(user)
        await self.session.commit()
        return response

    async def refresh(self, raw_token: str) -> TokenPairResponse:
        claims = self.codec.decode(raw_token, "refresh")
        record = await self.refresh_tokens.get_active(claims.jti, datetime.now(UTC))
        if record is None or record.token_hash != token_digest(raw_token):
            raise AuthenticationError("Refresh token is invalid or has already been used.")
        user = await self.users.get(claims.subject)
        if user is None or not user.is_active:
            raise AuthenticationError()

        record.revoked = True
        response = await self._issue_pair(user)
        replacement = self.codec.decode(response.refresh_token, "refresh")
        record.replaced_by_jti = replacement.jti
        await self.session.commit()
        return response

    async def _issue_pair(self, user: User) -> TokenPairResponse:
        access, _ = self.codec.issue(user.id, "access")
        refresh, claims = self.codec.issue(user.id, "refresh")
        self.refresh_tokens.add(
            RefreshToken(
                user_id=user.id,
                jti=claims.jti,
                token_hash=token_digest(refresh),
                expires_at=claims.expires_at,
                revoked=False,
                created_at=datetime.now(UTC),
            )
        )
        return TokenPairResponse(
            access_token=access,
            refresh_token=refresh,
            expires_in=self.settings.ACCESS_TOKEN_MINUTES * 60,
            user=UserResponse.model_validate(user),
        )
