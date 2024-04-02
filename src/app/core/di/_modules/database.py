from __future__ import annotations

import contextlib
from collections.abc import AsyncIterator

import aioinject
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from app.db import async_session_factory, engine
from lib.db import DBContext
from lib.types import Providers


@contextlib.asynccontextmanager
async def create_engine() -> AsyncIterator[AsyncEngine]:  # pragma: no cover
    try:
        yield engine
    except:
        await engine.dispose()
        raise


@contextlib.asynccontextmanager
async def create_session(
    _: AsyncEngine,
) -> AsyncIterator[AsyncSession]:  # pragma: no cover
    async with async_session_factory.begin() as session:
        yield session


async def db_context(session: AsyncSession) -> DBContext:
    return session


providers: Providers = [
    aioinject.Singleton(create_engine),
    aioinject.Scoped(create_session),
    aioinject.Scoped(db_context),
]
