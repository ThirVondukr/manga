from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.interfaces import ORMOption

from app.db.models import MangaBranch


class BranchRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get(
        self,
        id: UUID,
        options: Sequence[ORMOption] = (),
    ) -> MangaBranch | None:
        stmt = select(MangaBranch).where(MangaBranch.id == id).options(*options)
        return (await self._session.scalars(stmt)).one_or_none()
