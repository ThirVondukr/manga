import random
import uuid
from collections.abc import Sequence

from app.core.domain.manga.filters import MangaFilter, TagFilter
from app.core.domain.manga.repositories import MangaRepository
from app.db.models import Manga, MangaInfo, MangaTag
from lib.db import DBContext
from lib.pagination.pagination import PagePaginationParamsDTO
from lib.types import Language


async def test_get_ok(manga_repository: MangaRepository, manga: Manga) -> None:
    assert await manga_repository.get(id=manga.id) is manga


async def test_get_not_found(manga_repository: MangaRepository) -> None:
    assert await manga_repository.get(id=uuid.uuid4()) is None


async def test_filter_search_term(
    manga: Manga,
    manga_repository: MangaRepository,
    db_context: DBContext,
) -> None:
    manga.info = [
        MangaInfo(title="Search title", description="", language=Language.eng),
    ]
    db_context.add(manga)
    await db_context.flush()

    result = await manga_repository.paginate(
        filter=MangaFilter(search_term="not included"),
        pagination=PagePaginationParamsDTO(page=1, page_size=100),
    )
    assert result.items == []

    result = await manga_repository.paginate(
        filter=MangaFilter(search_term="Search"),
        pagination=PagePaginationParamsDTO(page=1, page_size=100),
    )
    assert result.items == [manga]


async def test_tags(
    manga_repository: MangaRepository,
    db_context: DBContext,
    manga: Manga,
    tags: Sequence[MangaTag],
) -> None:
    manga.tags = random.sample(tags, k=len(tags) // 2)
    assert manga.tags

    db_context.add(manga)
    await db_context.flush()
    pagination = PagePaginationParamsDTO(page=1, page_size=100)

    for tag in manga.tags:
        result = await manga_repository.paginate(
            filter=MangaFilter(tags=TagFilter(include=[tag.name_slug])),
            pagination=pagination,
        )
        assert result.items == [manga]

        result = await manga_repository.paginate(
            filter=MangaFilter(tags=TagFilter(exclude=[tag.name_slug])),
            pagination=pagination,
        )
        assert result.items == []

    for tag in tags:
        if tag in manga.tags:
            continue

        result = await manga_repository.paginate(
            filter=MangaFilter(tags=TagFilter(include=[tag.name_slug])),
            pagination=pagination,
        )
        assert result.items == []

        result = await manga_repository.paginate(
            filter=MangaFilter(tags=TagFilter(exclude=[tag.name_slug])),
            pagination=pagination,
        )
        assert result.items == [manga]
