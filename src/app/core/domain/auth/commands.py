from app.core.domain.auth.dto import SignInDTO
from app.core.domain.auth.services import AuthService, TokenService
from app.core.domain.users.dto import UserAuthResultDTO


class SignInCommand:
    def __init__(
        self,
        auth_service: AuthService,
        token_service: TokenService,
    ) -> None:
        self._auth_service = auth_service
        self._token_service = token_service

    async def execute(self, dto: SignInDTO) -> UserAuthResultDTO | None:
        user = await self._auth_service.authenticate(dto=dto)
        if user is None:
            return None

        return UserAuthResultDTO(
            user=user,
            access_token=self._token_service.create_access_token(user=user),
            refresh_token=self._token_service.create_refresh_token(user=user),
        )
