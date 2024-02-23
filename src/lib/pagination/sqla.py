from typing import TypeVar

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase

from lib.pagination.pagination import (
    PagePaginationInfoDTO,
    PagePaginationParamsDTO,
    PagePaginationResultDTO,
)

_TModel = TypeVar("_TModel", bound=DeclarativeBase)


async def page_paginate(
    *,
    stmt: Select[tuple[_TModel]],
    count_query: Select[tuple[int]] | None = None,
    session: AsyncSession,
    pagination: PagePaginationParamsDTO,
) -> PagePaginationResultDTO[_TModel]:
    items_query = stmt.limit(pagination.page_size).offset(
        (pagination.page - 1) * pagination.page_size,
    )
    items = (await session.scalars(items_query)).all()

    if count_query is None:
        count_query = select(func.count()).select_from(
            stmt.order_by(None).subquery(),
        )
    total_items = (await session.execute(count_query)).scalar_one()

    page_info = PagePaginationInfoDTO(
        current_page=pagination.page,
        page_size=pagination.page_size,
        total_items=total_items,
        has_next_page=pagination.page * pagination.page_size < total_items,
        has_previous_page=pagination.page > 1,
    )
    return PagePaginationResultDTO(
        items=items,
        page_info=page_info,
    )
