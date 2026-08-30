import hashlib
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any, Literal
from uuid import UUID, uuid4

import jwt
from jwt import ExpiredSignatureError, InvalidTokenError

from app.core.config import Settings
from app.exceptions.domain import AuthenticationError, TokenExpiredError


@dataclass(frozen=True, slots=True)
class TokenClaims:
    subject: UUID
    jti: str
    token_type: Literal["access", "refresh"]
    expires_at: datetime


class TokenCodec:
    def __init__(self, settings: Settings) -> None:
        self.secret = settings.SECRET_KEY.get_secret_value()
        self.algorithm = settings.JWT_ALGORITHM
        self.access_minutes = settings.ACCESS_TOKEN_MINUTES
        self.refresh_days = settings.REFRESH_TOKEN_DAYS

    def issue(
        self, user_id: UUID, token_type: Literal["access", "refresh"]
    ) -> tuple[str, TokenClaims]:
        now = datetime.now(UTC)
        delta = (
            timedelta(minutes=self.access_minutes)
            if token_type == "access"
            else timedelta(days=self.refresh_days)
        )
        expires_at = now + delta
        jti = uuid4().hex
        payload: dict[str, Any] = {
            "sub": str(user_id),
            "jti": jti,
            "typ": token_type,
            "iat": now,
            "exp": expires_at,
        }
        token = jwt.encode(payload, self.secret, algorithm=self.algorithm)
        return token, TokenClaims(user_id, jti, token_type, expires_at)

    def decode(self, token: str, expected_type: Literal["access", "refresh"]) -> TokenClaims:
        try:
            payload = jwt.decode(token, self.secret, algorithms=[self.algorithm])
            if payload.get("typ") != expected_type:
                raise AuthenticationError()
            return TokenClaims(
                subject=UUID(payload["sub"]),
                jti=str(payload["jti"]),
                token_type=expected_type,
                expires_at=datetime.fromtimestamp(payload["exp"], UTC),
            )
        except ExpiredSignatureError as exc:
            raise TokenExpiredError() from exc
        except (InvalidTokenError, KeyError, TypeError, ValueError) as exc:
            raise AuthenticationError() from exc


def token_digest(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()
