import pytest
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.domain.manga.manga.repositories import MangaRepository
from lib.db import DBContext
from tests.types import Resolver


@pytest.fixture
def db_context(session: AsyncSession) -> DBContext:
    return session


@pytest.fixture
async def crypt_context(resolver: Resolver) -> CryptContext:
    return await resolver(CryptContext)


@pytest.fixture
async def manga_repository(resolver: Resolver) -> MangaRepository:
    return await resolver(MangaRepository)
