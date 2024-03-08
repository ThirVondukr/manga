import pytest

from app.db.models import Group, Manga, MangaBranch
from lib.db import DBContext
from tests.factories import MangaBranchFactory


@pytest.fixture
async def manga_branch(
    manga: Manga,
    group: Group,
    db_context: DBContext,
) -> MangaBranch:
    branch = MangaBranchFactory.build(manga=manga, group=group)
    db_context.add(branch)
    await db_context.flush()
    return branch
