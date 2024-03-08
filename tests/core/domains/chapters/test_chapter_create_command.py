import uuid
from io import BytesIO
from pathlib import PurePath

import pytest

from app.core.domain.chapters.commands import ChapterCreateCommand
from app.core.domain.chapters.dto import ChapterCreateDTO
from app.db.models import Manga, MangaBranch, User
from app.settings import Buckets
from lib.files import File
from tests.types import Resolver
from tests.utils import TestImageStorage


@pytest.fixture
async def command(resolver: Resolver) -> ChapterCreateCommand:
    return await resolver(ChapterCreateCommand)


@pytest.fixture
def dto(manga_branch: MangaBranch) -> ChapterCreateDTO:
    file = File(
        buffer=BytesIO(),
        size=0,
        content_type="image/png",
        filename=PurePath("1.png"),
    )
    return ChapterCreateDTO(
        branch_id=manga_branch.id,
        title=str(uuid.uuid4()),
        volume=1,
        number=[1],
        pages=[file],
    )


async def test_ok(
    command: ChapterCreateCommand,
    user: User,
    dto: ChapterCreateDTO,
    s3_mock: TestImageStorage,
    manga: Manga,
) -> None:
    chapter = (await command.execute(dto, user)).unwrap()
    assert chapter.title == dto.title
    assert chapter.volume == dto.volume
    assert chapter.number == dto.number

    assert len(chapter.pages) == len(dto.pages)
    for chapter_page in chapter.pages:
        assert chapter_page.image_path in s3_mock.files

    assert s3_mock.files == [
        PurePath(
            Buckets.chapter_images,
            str(manga.id),
            str(chapter.id),
            p.filename,
        ).as_posix()
        for p in dto.pages
    ]
