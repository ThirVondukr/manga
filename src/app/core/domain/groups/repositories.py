from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Group


class GroupRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get(self, id: UUID) -> Group | None:
        return await self._session.get(Group, ident=id)

    async def exists(self, name: str) -> bool:
        stmt = select(Group).where(Group.name == name).exists()
        result: bool = (await self._session.scalars(stmt.select())).one()
        return result
