import dataclasses
import enum
from collections.abc import Sequence
from typing import Generic, TypeVar
from uuid import UUID

from app.db.models.manga import MangaBookmarkStatus
from lib.sort import SortDirection
from lib.types import MangaStatus

_T = TypeVar("_T")


class MangaSortField(enum.Enum):
    title = enum.auto()
    created_at = enum.auto()
    chapter_upload = enum.auto()


class MangaBookmarkSortField(enum.Enum):
    title = enum.auto()
    created_at = enum.auto()
    chapter_upload = enum.auto()
    bookmark_added_at = enum.auto()


@dataclasses.dataclass(frozen=True, kw_only=True, slots=True)
class Sort(Generic[_T]):
    field: _T
    direction: SortDirection


@dataclasses.dataclass
class TagFilter:
    include: list[UUID] | None = None
    exclude: list[UUID] | None = None


@dataclasses.dataclass
class MangaFilter:
    search_term: str | None = None
    statuses: Sequence[MangaStatus] | None = None
    tags: TagFilter = dataclasses.field(default_factory=TagFilter)


@dataclasses.dataclass
class MangaBookmarkFilter:
    manga: MangaFilter | None = None
    statuses: Sequence[MangaBookmarkStatus] | None = None


@dataclasses.dataclass
class MangaFindFilter:
    title: str | None = None
    title_slug: str | None = None
