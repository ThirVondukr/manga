from collections.abc import Sequence
from typing import Any

from sqlalchemy import ColumnElement, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.domain.users.filters import UserFilter
from app.db.models import User


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def exists(self, filter: UserFilter) -> bool:
        stmt = select(User).exists()
        if conditions := self._build_conditions(filter):
            stmt = stmt.where(or_(*conditions))
        result: bool = (await self._session.scalars(stmt.select())).one()
        return result

    def _build_conditions(
        self,
        /,
        filter: UserFilter,
    ) -> Sequence[ColumnElement[Any]]:
        conditions = []
        if filter.email is not None:
            conditions.append(User.email == filter.email)
        if filter.username is not None:
            conditions.append(User.username == filter.username)
        return conditions
