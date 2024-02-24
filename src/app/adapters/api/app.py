import contextlib
from collections.abc import AsyncIterator

from aioinject.ext.fastapi import AioInjectMiddleware
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app import sentry
from app.adapters.graphql.app import create_graphql_app
from app.core.di import create_container


def create_app() -> FastAPI:
    sentry.init_sentry()
    container = create_container()

    @contextlib.asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        async with contextlib.aclosing(container):
            yield

    app = FastAPI(lifespan=lifespan)
    app.add_middleware(AioInjectMiddleware, container=container)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_credentials=True,
    )

    @app.get("/health")
    async def healthcheck() -> None:
        return None

    app.mount("/graphql", create_graphql_app())

    return app
