import pytest

from app.db.models import Manga, MangaBranch
from lib.db import DBContext
from tests.factories import MangaBranchFactory


@pytest.fixture
async def manga_branch(manga: Manga, db_context: DBContext) -> MangaBranch:
    branch = MangaBranchFactory.build(manga=manga)
    db_context.add(branch)
    await db_context.flush()
    return branch
