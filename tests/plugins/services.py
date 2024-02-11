import pytest
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from lib.db import DBContext
from tests.types import Resolver


@pytest.fixture
def db_context(session: AsyncSession) -> DBContext:
    return session


@pytest.fixture
async def crypt_context(resolver: Resolver) -> CryptContext:
    return await resolver(CryptContext)
