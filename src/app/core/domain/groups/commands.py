from result import Result

from app.core.domain.groups.dto import GroupCreateDTO
from app.core.domain.groups.services import GroupService
from app.core.errors import EntityAlreadyExistsError
from app.db.models import Group, User


class GroupCreateCommand:
    def __init__(self, group_service: GroupService) -> None:
        self._group_service = group_service

    async def execute(
        self,
        dto: GroupCreateDTO,
        user: User,
    ) -> Result[Group, EntityAlreadyExistsError]:
        return await self._group_service.create(dto=dto, user=user)
