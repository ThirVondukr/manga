import itertools
import random
import uuid
from collections.abc import Sequence
from datetime import datetime

import pytest

from app.core.domain.manga.filters import (
    MangaFilter,
    MangaSortField,
    Sort,
    TagFilter,
)
from app.core.domain.manga.repositories import MangaRepository
from app.db.models import AltTitle, Group, Manga, MangaTag, User
from lib.db import DBContext
from lib.pagination.pagination import PagePaginationParamsDTO
from lib.sort import SortDirection
from lib.types import Language, MangaStatus
from tests.factories import ChapterFactory, MangaBranchFactory, MangaFactory


async def test_get_ok(manga_repository: MangaRepository, manga: Manga) -> None:
    assert await manga_repository.get(id=manga.id) is manga


async def test_get_not_found(manga_repository: MangaRepository) -> None:
    assert await manga_repository.get(id=uuid.uuid4()) is None


_DEFAULT_SORT: Sort[MangaSortField] = Sort(
    field=MangaSortField.title,
    direction=SortDirection.desc,
)


async def test_filter_search_term(
    manga: Manga,
    manga_repository: MangaRepository,
    db_context: DBContext,
) -> None:
    manga.alt_titles = [
        AltTitle(title="Search title", language=Language.eng),
    ]
    db_context.add(manga)
    await db_context.flush()

    result = await manga_repository.paginate(
        filter=MangaFilter(search_term="not included"),
        pagination=PagePaginationParamsDTO(page=1, page_size=100),
        sort=_DEFAULT_SORT,
    )
    assert result.items == []

    result = await manga_repository.paginate(
        filter=MangaFilter(search_term="Search"),
        pagination=PagePaginationParamsDTO(page=1, page_size=100),
        sort=_DEFAULT_SORT,
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
            sort=_DEFAULT_SORT,
        )
        assert result.items == [manga]

        result = await manga_repository.paginate(
            filter=MangaFilter(tags=TagFilter(exclude=[tag.name_slug])),
            pagination=pagination,
            sort=_DEFAULT_SORT,
        )
        assert result.items == []

    for tag in tags:
        if tag in manga.tags:
            continue

        result = await manga_repository.paginate(
            filter=MangaFilter(tags=TagFilter(include=[tag.name_slug])),
            pagination=pagination,
            sort=_DEFAULT_SORT,
        )
        assert result.items == []

        result = await manga_repository.paginate(
            filter=MangaFilter(tags=TagFilter(exclude=[tag.name_slug])),
            pagination=pagination,
            sort=_DEFAULT_SORT,
        )
        assert result.items == [manga]


async def test_filter_by_status(
    manga_repository: MangaRepository,
    db_context: DBContext,
) -> None:
    mangas = {status: MangaFactory(status=status) for status in MangaStatus}
    db_context.add_all(mangas.values())
    await db_context.flush()

    for status, manga in mangas.items():
        result = await manga_repository.paginate(
            filter=MangaFilter(status=status),
            pagination=PagePaginationParamsDTO(page=1, page_size=100),
            sort=_DEFAULT_SORT,
        )
        assert result.items == [manga]


@pytest.mark.parametrize(
    ("direction", "sort_field"),
    itertools.product(
        SortDirection,
        [MangaSortField.title, MangaSortField.created_at],
    ),
)
async def test_sort(
    mangas: Sequence[Manga],
    direction: SortDirection,
    sort_field: MangaSortField,
    manga_repository: MangaRepository,
) -> None:
    expected = sorted(
        mangas,
        key=lambda m: (getattr(m, sort_field.name), m.id),
        reverse=direction is SortDirection.desc,
    )

    result = await manga_repository.paginate(
        pagination=PagePaginationParamsDTO(page=1, page_size=100),
        sort=Sort(field=sort_field, direction=direction),
    )
    assert result.items == expected


@pytest.mark.parametrize(
    "direction",
    SortDirection,
)
async def test_sort_by_latest_chapter_upload_date(  # noqa: PLR0913
    mangas: Sequence[Manga],
    direction: SortDirection,
    manga_repository: MangaRepository,
    group: Group,
    chapter_factory: ChapterFactory,
    db_context: DBContext,
    user: User,
) -> None:
    manga_latest_chapter_dates = {}
    for manga in mangas:
        branch = MangaBranchFactory(group=group, manga=manga)
        branch.chapters = [
            chapter_factory(branch=branch, created_by=user)
            for _ in range(random.randint(0, 5))
        ]
        manga.branches.append(branch)
        manga_latest_chapter_dates[manga.id] = (
            max(c.created_at for c in branch.chapters)
            if branch.chapters
            else None
        )
        db_context.add(manga)
    await db_context.flush()

    expected = sorted(
        mangas,
        key=lambda manga: (
            manga_latest_chapter_dates[manga.id] or datetime.min,
            manga.id,
        ),
        reverse=direction is SortDirection.desc,
    )
    # Push null values to end
    expected.sort(key=lambda m: manga_latest_chapter_dates[m.id] is None)

    result = await manga_repository.paginate(
        filter=MangaFilter(),
        pagination=PagePaginationParamsDTO(page=1, page_size=100),
        sort=Sort(field=MangaSortField.chapter_upload, direction=direction),
    )
    assert len(result.items) == len(mangas)
    assert result.items == expected
