from result import Result

from app.core.domain.users.dto import UserRegisterDTO
from app.core.domain.users.errors import UserAlreadyExistsError
from app.core.domain.users.services import UserService
from app.db.models import User


class UserRegisterCommand:
    def __init__(self, service: UserService) -> None:
        self._service = service

    async def execute(
        self,
        dto: UserRegisterDTO,
    ) -> Result[User, UserAlreadyExistsError]:
        return await self._service.register(dto=dto)
