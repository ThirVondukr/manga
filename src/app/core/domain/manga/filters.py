import dataclasses


@dataclasses.dataclass
class TagFilter:
    include: list[str] | None = None
    exclude: list[str] | None = None


@dataclasses.dataclass
class MangaFilter:
    search_term: str | None = None
    tags: TagFilter = dataclasses.field(default_factory=TagFilter)
