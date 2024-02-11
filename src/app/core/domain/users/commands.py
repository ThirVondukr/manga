from result import Err, Ok, Result

from app.core.domain.auth.dto import UserAuthResultDTO, UserRegisterDTO
from app.core.domain.auth.services import AuthService, TokenService
from app.core.domain.users.errors import UserAlreadyExistsError


class UserRegisterCommand:
    def __init__(
        self,
        auth_service: AuthService,
        token_service: TokenService,
    ) -> None:
        self._auth_service = auth_service
        self._token_service = token_service

    async def execute(
        self,
        dto: UserRegisterDTO,
    ) -> Result[UserAuthResultDTO, UserAlreadyExistsError]:
        user = await self._auth_service.sign_up(dto=dto)
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
