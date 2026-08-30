import importlib.util
import logging

from app.core.config import Settings

logger = logging.getLogger("parkgo.observability")


def configure_optional_sentry(settings: Settings) -> None:
    if not settings.SENTRY_DSN:
        return
    if importlib.util.find_spec("sentry_sdk") is None:
        logger.warning("sentry_dsn_configured_but_sdk_not_installed")
        return
    import sentry_sdk  # type: ignore[import-not-found]

    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.APP_ENV,
        send_default_pii=False,
        traces_sample_rate=0.05,
    )
