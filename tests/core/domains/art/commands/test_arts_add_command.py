import uuid

import pytest

from app.core.domain.manga.art.command import AddArtsToMangaCommand
from app.core.domain.manga.art.dto import MangaArtAddDTO, MangaArtsAddDTO
from app.core.errors import (
    EntityAlreadyExistsError,
    NotFoundError,
    PermissionDeniedError,
)
from app.db.models import User
from app.db.models.manga import Manga
from lib.types import Language
from tests.factories import MangaArtFactory
from tests.types import Resolver
from tests.utils import create_dummy_image_file


@pytest.fixture
async def command(resolver: Resolver) -> AddArtsToMangaCommand:
    return await resolver(AddArtsToMangaCommand)


@pytest.fixture
async def dto(manga: Manga) -> MangaArtsAddDTO:
    return MangaArtsAddDTO(
        manga_id=manga.id,
        arts=[
            MangaArtAddDTO(
                image=create_dummy_image_file(),
                volume=i,
                language=Language.eng,
            )
            for i in range(5)
        ],
    )


async def test_not_found(
    command: AddArtsToMangaCommand,
    dto: MangaArtsAddDTO,
    user: User,
) -> None:
    dto.manga_id = uuid.uuid4()
    result = await command.execute(user=user, dto=dto)
    assert result.unwrap_err() == NotFoundError(entity_id=str(dto.manga_id))


async def test_permission_denied(
    command: AddArtsToMangaCommand,
    dto: MangaArtsAddDTO,
    user: User,
) -> None:
    result = await command.execute(user=user, dto=dto)
    assert result.unwrap_err() == PermissionDeniedError()


@pytest.mark.usefixtures("make_user_superuser")
async def test_duplicate_art(
    command: AddArtsToMangaCommand,
    dto: MangaArtsAddDTO,
    user: User,
    manga: Manga,
) -> None:
    manga.arts = [MangaArtFactory(manga=manga, volume=1, language=Language.eng)]
    result = await command.execute(user=user, dto=dto)
    assert result.unwrap_err() == EntityAlreadyExistsError()


@pytest.mark.usefixtures("make_user_superuser")
async def test_ok(
    command: AddArtsToMangaCommand,
    dto: MangaArtsAddDTO,
    user: User,
    manga: Manga,
) -> None:
    result = await command.execute(user=user, dto=dto)
    assert result.unwrap() == manga
