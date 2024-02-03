import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from lib.db import DBContext


@pytest.fixture
def db_context(session: AsyncSession) -> DBContext:
    return session
