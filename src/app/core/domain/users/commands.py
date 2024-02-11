from result import Err, Ok, Result

from app.core.domain.auth.services import TokenService
from app.core.domain.users.dto import UserAuthResultDTO, UserRegisterDTO
from app.core.domain.users.errors import UserAlreadyExistsError
from app.core.domain.users.services import UserService


class UserRegisterCommand:
    def __init__(
        self,
        user_service: UserService,
        token_service: TokenService,
    ) -> None:
        self._user_service = user_service
        self._token_service = token_service

    async def execute(
        self,
        dto: UserRegisterDTO,
    ) -> Result[UserAuthResultDTO, UserAlreadyExistsError]:
        user = await self._user_service.register(dto=dto)
        if isinstance(user, Err):
            return user

        result = UserAuthResultDTO(
            user=user.ok_value,
            access_token=self._token_service.create_access_token(
                user=user.ok_value,
            ),
            refresh_token=self._token_service.create_refresh_token(
                user=user.ok_value,
            ),
        )
        return Ok(result)
