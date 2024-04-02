import logging

from app.settings import SentrySettings
from lib.settings import get_settings


def init_sentry() -> None:
    import sentry_sdk

    settings = get_settings(SentrySettings)
    sentry_sdk.init(
        dsn=settings.dsn,
        environment=settings.environment.name,
        traces_sample_rate=settings.traces_sample_rate,
    )


def setup_logging() -> None:  # pragma: no cover
    logging.basicConfig(level=logging.INFO)
