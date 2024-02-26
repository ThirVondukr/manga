from result import Err

from app.core.domain.auth.dto import SignInDTO, TokenClaims, UserAuthResultDTO
from app.core.domain.auth.services import AuthService, TokenService


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


class AuthenticateAccessTokenCommand:
    def __init__(self, token_service: TokenService) -> None:
        self._token_service = token_service

    async def execute(self, token: str | None) -> TokenClaims | None:
        if not token or not token.startswith("Bearer "):
            return None

        token = token.removeprefix("Bearer ")

        claims = self._token_service.decode(token=token)
        if isinstance(claims, Err):  # pragma: no cover
            return None

        if (  # pragma: no cover
            claims.ok_value.token_type != "access"  # noqa: S105
        ):
            return None

        return claims.ok_value
