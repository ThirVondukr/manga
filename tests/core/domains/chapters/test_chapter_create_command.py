import uuid
from io import BytesIO
from pathlib import PurePath

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.domain.chapters.commands import ChapterCreateCommand
from app.core.domain.chapters.dto import ChapterCreateDTO
from app.core.errors import (
    EntityAlreadyExistsError,
    PermissionDeniedError,
    RelationshipNotFoundError,
)
from app.db.models import Group, Manga, MangaBranch, MangaChapter, User
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


async def test_branch_not_found(
    command: ChapterCreateCommand,
    user: User,
    dto: ChapterCreateDTO,
) -> None:
    dto.branch_id = uuid.uuid4()
    err = (await command.execute(dto, user)).unwrap_err()
    assert err == RelationshipNotFoundError(entity_id=str(dto.branch_id))


async def test_permission_denied(
    command: ChapterCreateCommand,
    user: User,
    other_user: User,
    session: AsyncSession,
    dto: ChapterCreateDTO,
    group: Group,
) -> None:
    group.created_by = other_user
    session.add(group)

    err = (await command.execute(dto, user)).unwrap_err()
    assert err == PermissionDeniedError()


async def test_duplicate_chapter_number(
    command: ChapterCreateCommand,
    user: User,
    dto: ChapterCreateDTO,
) -> None:
    dto.number = [1]

    chapter = (await command.execute(dto, user)).unwrap()
    assert isinstance(chapter, MangaChapter)

    err = (await command.execute(dto, user)).unwrap_err()
    assert err == EntityAlreadyExistsError()


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
