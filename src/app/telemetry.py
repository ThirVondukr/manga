import logging

from app.settings import SentrySettings
from lib.settings import get_settings


def setup_telemetry() -> None:
    import sentry_sdk

    settings = get_settings(SentrySettings)
    sentry_sdk.init(
        dsn=settings.dsn,
        environment=settings.environment.name,
        traces_sample_rate=settings.traces_sample_rate,
    )
    logging.basicConfig(level=logging.INFO)
