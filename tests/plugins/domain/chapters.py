import pytest

from app.core.domain.manga.chapters.services import ChapterService
from app.db.models import User
from app.db.models.manga import MangaBranch, MangaChapter
from lib.db import DBContext
from tests.types import Resolver


@pytest.fixture
async def manga_chapter(
    manga_branch: MangaBranch,
    db_context: DBContext,
    user: User,
) -> MangaChapter:
    chapter = MangaChapter(
        title="Title",
        branch=manga_branch,
        created_by=user,
        pages=[],
        number=[1],
        volume=None,
    )
    db_context.add(chapter)
    return chapter


@pytest.fixture
async def chapter_service(resolver: Resolver) -> ChapterService:
    return await resolver(ChapterService)
