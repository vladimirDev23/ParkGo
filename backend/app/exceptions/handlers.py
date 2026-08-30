import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from app.exceptions.domain import AppError

logger = logging.getLogger("parkgo.errors")


def error_payload(code: str, message: str, details: object | None = None) -> dict[str, object]:
    return {"error": {"code": code, "message": message, "details": details or {}}}


def install_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def handle_app_error(request: Request, exc: AppError) -> JSONResponse:
        if exc.code in {"PROVIDER_UNAVAILABLE", "PAYMENT_FAILED", "INVALID_ZONE"}:
            logger.warning(
                "provider_operation_failed",
                extra={
                    "request_id": getattr(request.state, "request_id", None),
                    "endpoint": request.url.path,
                    "status": exc.status_code,
                },
            )
        return JSONResponse(
            status_code=exc.status_code,
            content=error_payload(exc.code, exc.message, exc.details),
        )

    @app.exception_handler(RequestValidationError)
    async def handle_validation(_: Request, exc: RequestValidationError) -> JSONResponse:
        fields = [
            {"field": ".".join(str(part) for part in error["loc"]), "message": error["msg"]}
            for error in exc.errors()
        ]
        return JSONResponse(
            status_code=422,
            content=error_payload(
                "VALIDATION_ERROR", "Проверьте введённые данные.", {"fields": fields}
            ),
        )

    @app.exception_handler(IntegrityError)
    async def handle_integrity(request: Request, exc: IntegrityError) -> JSONResponse:
        logger.warning("database_integrity_error", extra={"path": request.url.path})
        return JSONResponse(
            status_code=409,
            content=error_payload("CONFLICT", "Данные конфликтуют с существующей записью."),
        )

    @app.exception_handler(Exception)
    async def handle_unexpected(request: Request, exc: Exception) -> JSONResponse:
        request_id = getattr(request.state, "request_id", None)
        logger.exception(
            "unhandled_error",
            extra={"path": request.url.path, "request_id": request_id},
        )
        return JSONResponse(
            status_code=500,
            content=error_payload(
                "INTERNAL_ERROR",
                "Произошла внутренняя ошибка. Попробуйте ещё раз.",
                {"request_id": request_id} if request_id else {},
            ),
        )
