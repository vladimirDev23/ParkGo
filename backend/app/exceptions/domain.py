from __future__ import annotations

from typing import Any


class AppError(Exception):
    code = "APPLICATION_ERROR"
    status_code = 400
    default_message = "Не удалось выполнить операцию."

    def __init__(
        self, message: str | None = None, *, details: dict[str, Any] | None = None
    ) -> None:
        super().__init__(message or self.default_message)
        self.message = message or self.default_message
        self.details = details or {}


class AuthenticationError(AppError):
    code = "AUTHENTICATION_REQUIRED"
    status_code = 401
    default_message = "Требуется повторный вход."


class InvalidCredentialsError(AuthenticationError):
    code = "INVALID_CREDENTIALS"
    default_message = "Неверный email или пароль."


class TokenExpiredError(AuthenticationError):
    code = "TOKEN_EXPIRED"
    default_message = "Сессия истекла. Войдите снова."


class PermissionDeniedError(AppError):
    code = "PERMISSION_DENIED"
    status_code = 403
    default_message = "Недостаточно прав для этой операции."


class ResourceNotFoundError(AppError):
    code = "NOT_FOUND"
    status_code = 404
    default_message = "Объект не найден."


class ConflictError(AppError):
    code = "CONFLICT"
    status_code = 409


class EmailAlreadyRegisteredError(ConflictError):
    code = "EMAIL_ALREADY_REGISTERED"
    default_message = "Пользователь с таким email уже зарегистрирован."


class VehicleNotFoundError(ResourceNotFoundError):
    code = "VEHICLE_NOT_FOUND"
    default_message = "Автомобиль не найден."


class VehicleInActiveSessionError(ConflictError):
    code = "VEHICLE_IN_ACTIVE_SESSION"
    default_message = "Нельзя удалить автомобиль с активной парковкой."


class ParkingZoneNotFoundError(ResourceNotFoundError):
    code = "PARKING_ZONE_NOT_FOUND"
    default_message = "Парковочная зона не найдена."


class ParkingSessionNotFoundError(ResourceNotFoundError):
    code = "PARKING_SESSION_NOT_FOUND"
    default_message = "Парковочная сессия не найдена."


class SessionAlreadyActiveError(ConflictError):
    code = "SESSION_ALREADY_ACTIVE"
    default_message = "У вас уже есть активная парковка."


class ProviderUnavailableError(AppError):
    code = "PROVIDER_UNAVAILABLE"
    status_code = 503
    default_message = "Не удалось связаться с парковочной системой. Попробуйте ещё раз."


class InvalidZoneError(AppError):
    code = "INVALID_ZONE"
    status_code = 422
    default_message = "Эта парковочная зона сейчас недоступна."


class PaymentFailedError(AppError):
    code = "PAYMENT_FAILED"
    status_code = 402
    default_message = "Не удалось выполнить тестовую оплату. Попробуйте ещё раз."


class VehicleNotAllowedError(AppError):
    code = "VEHICLE_NOT_ALLOWED"
    status_code = 422
    default_message = "Этот автомобиль нельзя использовать для выбранной парковки."


class RateLimitExceededError(AppError):
    code = "RATE_LIMIT_EXCEEDED"
    status_code = 429
    default_message = "Слишком много попыток. Попробуйте немного позже."
