import dataclasses

from lib.types import MangaStatus


@dataclasses.dataclass
class TagFilter:
    include: list[str] | None = None
    exclude: list[str] | None = None


@dataclasses.dataclass
class MangaFilter:
    search_term: str | None = None
    status: MangaStatus | None = None
    tags: TagFilter = dataclasses.field(default_factory=TagFilter)


@dataclasses.dataclass
class MangaFindFilter:
    title: str | None = None
    title_slug: str | None = None
