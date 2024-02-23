import dataclasses
import math
from typing import Generic, Self, TypeVar

import strawberry
from sqlalchemy.orm import DeclarativeBase

from app.adapters.graphql.dto import DTOMixinProtocol
from lib.pagination.pagination import (
    PagePaginationInfoDTO,
    PagePaginationParamsDTO,
    PagePaginationResultDTO,
)

T = TypeVar("T")
V = TypeVar("V")
TModel = TypeVar("TModel", bound=DeclarativeBase)
TType = TypeVar("TType")


@strawberry.input(name="PagePaginationInput")
@dataclasses.dataclass(frozen=True)
class PagePaginationInputGQL:
    page: int = 1
    page_size: int = 100

    def to_dto(self) -> PagePaginationParamsDTO:
        return PagePaginationParamsDTO(
            page=self.page,
            page_size=self.page_size,
        )


@strawberry.type(name="PagePaginationInfo")
class PagePaginationInfo:
    current_page: int
    page_size: int
    total_items: int
    has_next_page: bool
    has_previous_page: bool

    @strawberry.field
    def total_pages(self) -> int:
        return math.ceil(self.total_items / self.page_size)

    @classmethod
    def from_dto(cls, dto: PagePaginationInfoDTO) -> Self:
        return cls(
            current_page=dto.current_page,
            page_size=dto.page_size,
            total_items=dto.total_items,
            has_next_page=dto.has_next_page,
            has_previous_page=dto.has_previous_page,
        )


@strawberry.type(name="PagePaginationResult")
class PagePaginationResultGQL(Generic[T]):
    items: list[T]
    page_info: PagePaginationInfo


def map_page_pagination(
    pagination: PagePaginationResultDTO[T],
    model_cls: type[DTOMixinProtocol[T, V]],
) -> PagePaginationResultGQL[V]:
    return PagePaginationResultGQL(
        items=model_cls.from_dto_list(pagination.items),
        page_info=PagePaginationInfo.from_dto(pagination.page_info),
    )
