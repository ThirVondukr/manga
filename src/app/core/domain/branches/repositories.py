from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import MangaBranch


class BranchRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get(self, id: UUID) -> MangaBranch | None:
        return await self._session.get(MangaBranch, ident=id)
