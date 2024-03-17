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
from tests.utils import casefold_obj


async def test_get_ok(manga_repository: MangaRepository, manga: Manga) -> None:
    assert await manga_repository.get(id=manga.id) is manga


async def test_get_not_found(manga_repository: MangaRepository) -> None:
    assert await manga_repository.get(id=uuid.uuid4()) is None


_DEFAULT_SORT: Sort[MangaSortField] = Sort(
    field=MangaSortField.title,
    direction=SortDirection.desc,
)


@pytest.mark.parametrize(
    ("title", "search_term", "should_include"),
    [
        ("Title", "title", True),
        ("Title", "  Title ", True),
        ("Title", "something different", False),
    ],
)
async def test_filter_search_term(
    manga: Manga,
    manga_repository: MangaRepository,
    db_context: DBContext,
    title: str,
    search_term: str,
    should_include: bool,
) -> None:
    manga.title = title
    db_context.add(manga)

    result = await manga_repository.paginate(
        filter=MangaFilter(search_term=search_term),
        pagination=PagePaginationParamsDTO(page=1, page_size=100),
        sort=_DEFAULT_SORT,
    )
    assert result.items == ([manga] if should_include else [])


@pytest.mark.parametrize(
    ("title", "search_term", "should_include"),
    [
        ("Title", "title", True),
        ("Title", "  Title ", True),
        ("Title", "something different", False),
    ],
)
async def test_filter_search_term_alt_title(
    manga: Manga,
    manga_repository: MangaRepository,
    db_context: DBContext,
    title: str,
    search_term: str,
    should_include: bool,
) -> None:
    manga.alt_titles = [
        AltTitle(title=title, language=Language.eng),
    ]
    db_context.add(manga)

    result = await manga_repository.paginate(
        filter=MangaFilter(search_term=search_term),
        pagination=PagePaginationParamsDTO(page=1, page_size=100),
        sort=_DEFAULT_SORT,
    )
    assert result.items == ([manga] if should_include else [])


async def test_tags(
    manga_repository: MangaRepository,
    db_context: DBContext,
    manga: Manga,
    tags: Sequence[MangaTag],
) -> None:
    manga.tags = random.sample(tags, k=len(tags) // 2)
    assert manga.tags

    db_context.add(manga)
    pagination = PagePaginationParamsDTO(page=1, page_size=100)

    for tag in manga.tags:
        result = await manga_repository.paginate(
            filter=MangaFilter(tags=TagFilter(include=[tag.id])),
            pagination=pagination,
            sort=_DEFAULT_SORT,
        )
        assert result.items == [manga]

        result = await manga_repository.paginate(
            filter=MangaFilter(tags=TagFilter(exclude=[tag.id])),
            pagination=pagination,
            sort=_DEFAULT_SORT,
        )
        assert result.items == []

    for tag in tags:
        if tag in manga.tags:
            continue

        result = await manga_repository.paginate(
            filter=MangaFilter(tags=TagFilter(include=[tag.id])),
            pagination=pagination,
            sort=_DEFAULT_SORT,
        )
        assert result.items == []

        result = await manga_repository.paginate(
            filter=MangaFilter(tags=TagFilter(exclude=[tag.id])),
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

    for status, manga in mangas.items():
        result = await manga_repository.paginate(
            filter=MangaFilter(statuses=[status]),
            pagination=PagePaginationParamsDTO(page=1, page_size=100),
            sort=_DEFAULT_SORT,
        )
        assert result.items == [manga]


@pytest.mark.parametrize(
    ("direction", "sort_field"),
    itertools.product(
        SortDirection,
        [s for s in MangaSortField if s is not MangaSortField.chapter_upload],
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
        key=lambda m: (casefold_obj(getattr(m, sort_field.name)), m.id),
        reverse=direction is SortDirection.desc,
    )
    expected.sort(key=lambda m: getattr(m, sort_field.name) is None)

    result = await manga_repository.paginate(
        pagination=PagePaginationParamsDTO(page=1, page_size=100),
        sort=Sort(field=sort_field, direction=direction),
    )
    assert [m.id for m in result.items] == [m.id for m in expected]


@pytest.mark.parametrize(
    "direction",
    SortDirection,
)
async def test_sort_by_latest_chapter_upload_date(
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
        if random.random() >= 0.5:  # noqa: PLR2004
            continue
        branch = MangaBranchFactory(group=group, manga=manga)
        chapter = chapter_factory(branch=branch, created_by=user)
        branch.chapters = [chapter]
        manga.branches.append(branch)
        manga_latest_chapter_dates[manga.id] = chapter.created_at
        manga.latest_chapter_id = chapter.id
        db_context.add(manga)

    expected = sorted(
        mangas,
        key=lambda manga: (
            manga_latest_chapter_dates.get(manga.id, datetime.min)
            or datetime.min,
            manga.id,
        ),
        reverse=direction is SortDirection.desc,
    )
    # Push null values to end
    expected.sort(key=lambda m: manga_latest_chapter_dates.get(m.id) is None)

    result = await manga_repository.paginate(
        filter=MangaFilter(),
        pagination=PagePaginationParamsDTO(page=1, page_size=100),
        sort=Sort(field=MangaSortField.chapter_upload, direction=direction),
    )
    assert result.items == expected
