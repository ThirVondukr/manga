import contextlib
from collections.abc import AsyncIterator

from aioinject.ext.fastapi import AioInjectMiddleware
from fastapi import FastAPI
from litestar.types import ASGIApp, Receive, Scope, Send
from starlette.middleware.cors import CORSMiddleware

from app import telemetry
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


def create_app() -> FastAPI:
    telemetry.setup_telemetry()
    container = create_container()
    _app_settings = get_settings(AppSettings)

    @contextlib.asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        async with container:
            yield

    app = FastAPI(lifespan=lifespan)

    app.mount("/graphql", create_graphql_app())

    app.add_middleware(
        CORSMiddleware,
        allow_origins=_app_settings.cors_allow_origins,
        allow_methods=_app_settings.cors_allow_methods,
        allow_headers=_app_settings.cors_allow_headers,
    )
    app.add_middleware(AioInjectMiddleware, container=container)

    @app.get("/health")
    async def healthcheck() -> None:
        return None

    return app


_app = create_app()
