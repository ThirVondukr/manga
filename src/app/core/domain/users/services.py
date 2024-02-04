from result import Err, Ok, Result

from app.core.domain.users.dto import UserRegisterDTO
from app.core.domain.users.errors import UserAlreadyExistsError
from app.core.domain.users.filters import UserFilter
from app.core.domain.users.repositories import UserRepository
from app.db.models import User
from lib.db import DBContext


class UserService:
    def __init__(
        self,
        repository: UserRepository,
        db_context: DBContext,
    ) -> None:
        self._repository = repository
        self._db = db_context

    async def register(
        self,
        dto: UserRegisterDTO,
    ) -> Result[User, UserAlreadyExistsError]:
        if await self._repository.exists(
            UserFilter(username=dto.username, email=dto.email),
        ):
            return Err(UserAlreadyExistsError())
        user = User(
            email=dto.email,
            username=dto.username,
            password_hash=dto.password.get_secret_value(),
        )
        self._db.add(user)
        await self._db.flush()
        return Ok(user)
