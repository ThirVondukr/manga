import dataclasses
import enum
from collections.abc import Sequence
from typing import Generic, TypeVar
from uuid import UUID

from lib.sort import SortDirection
from lib.types import MangaStatus

_T = TypeVar("_T")


class MangaSortField(enum.Enum):
    title = enum.auto()
    created_at = enum.auto()
    chapter_upload = enum.auto()


@dataclasses.dataclass
class Sort(Generic[_T]):
    field: MangaSortField
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
class MangaFindFilter:
    title: str | None = None
    title_slug: str | None = None
