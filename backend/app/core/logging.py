import json
import logging
from datetime import UTC, datetime
from typing import Any, ClassVar


class JSONFormatter(logging.Formatter):
    protected_fields: ClassVar[set[str]] = {
        "password",
        "password_hash",
        "token",
        "access_token",
        "refresh_token",
    }

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname.lower(),
            "logger": record.name,
            "message": record.getMessage(),
        }
        for field in ("request_id", "user_id", "provider", "endpoint", "status", "duration_ms"):
            value = getattr(record, field, None)
            if value is not None:
                payload[field] = value
        if record.exc_info:
            exception_type = record.exc_info[0]
            payload["exception"] = exception_type.__name__ if exception_type else "Exception"
        return json.dumps(payload, ensure_ascii=False, default=str)


def configure_logging(debug: bool = False) -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(JSONFormatter())
    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(logging.DEBUG if debug else logging.INFO)
