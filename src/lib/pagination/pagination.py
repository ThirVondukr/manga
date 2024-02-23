import dataclasses
from collections.abc import Sequence
from typing import Generic, TypeVar

_T = TypeVar("_T")


class PaginationError(Exception):
    pass


@dataclasses.dataclass(slots=True, kw_only=True)
class PagePaginationParamsDTO:
    page: int
    page_size: int

    def __post_init__(self) -> None:
        if self.page <= 0:
            msg = f"Page should be greater than 0, got {self.page}"
            raise PaginationError(msg)

        if self.page_size <= 0:
            msg = f"Page size should be greater than 0, got {self.page_size}"
            raise PaginationError(msg)


@dataclasses.dataclass(slots=True, kw_only=True)
class PagePaginationInfoDTO:
    current_page: int
    page_size: int

    total_items: int
    has_next_page: bool
    has_previous_page: bool


@dataclasses.dataclass(slots=True, kw_only=True)
class PagePaginationResultDTO(Generic[_T]):
    items: Sequence[_T]
    page_info: PagePaginationInfoDTO
