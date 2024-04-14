import contextlib
from collections.abc import AsyncIterator

from aioinject.ext.litestar import AioInjectPlugin
from litestar import Litestar, asgi, get
from litestar.config.cors import CORSConfig
from litestar.types import ASGIApp, Receive, Scope, Send

from app import sentry
from app.adapters.graphql.app import create_graphql_app
from app.core.di import create_container
from app.settings import AppSettings
from lib.settings import get_settings


class _MountWrapper:
    def __init__(self, app: ASGIApp) -> None:
        self._app = app

    async def __call__(
        self,
        scope: Scope,
        receive: Receive,
        send: Send,
    ) -> None:
        await self._app(scope, receive, send)


def create_app() -> Litestar:
    sentry.init_sentry()
    container = create_container()
    _app_settings = get_settings(AppSettings)

    @contextlib.asynccontextmanager
    async def lifespan(_: Litestar) -> AsyncIterator[None]:
        async with contextlib.aclosing(container):
            yield

    cors_config = CORSConfig(
        allow_origins=_app_settings.cors_allow_origins,
        allow_methods=_app_settings.cors_allow_methods,
        allow_headers=_app_settings.cors_allow_headers,
        allow_credentials=True,
    )

    @get("/health")
    async def healthcheck() -> None:
        return None

    return Litestar(
        lifespan=[lifespan],
        plugins=[AioInjectPlugin(container=container)],
        cors_config=cors_config,
        route_handlers=[
            asgi("/graphql", is_mount=True)(
                _MountWrapper(create_graphql_app()),  # type: ignore[arg-type]
            ),
            healthcheck,
        ],
    )


_app = create_app()
