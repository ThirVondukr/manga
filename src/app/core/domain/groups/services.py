from result import Err, Ok, Result

from app.core.domain.groups.dto import GroupCreateDTO
from app.core.domain.groups.repositories import GroupRepository
from app.core.errors import EntityAlreadyExistsError
from app.db.models import Group, User
from lib.db import DBContext


class GroupService:
    def __init__(
        self,
        db_context: DBContext,
        repository: GroupRepository,
    ) -> None:
        self._db_context = db_context
        self._repository = repository

    async def create(
        self,
        dto: GroupCreateDTO,
        user: User,
    ) -> Result[Group, EntityAlreadyExistsError]:
        if await self._repository.exists(name=dto.name):
            return Err(EntityAlreadyExistsError())

        group = Group(
            name=dto.name,
            created_by=user,
        )
        self._db_context.add(group)
        await self._db_context.flush()
        return Ok(group)
