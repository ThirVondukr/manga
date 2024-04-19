from result import Err

from app.core.domain.auth.dto import TokenClaims
from app.core.domain.auth.services import TokenService
from app.core.domain.users.services import UserService


class AuthenticateAccessTokenCommand:
    def __init__(
        self,
        token_service: TokenService,
        user_service: UserService,
    ) -> None:
        self._token_service = token_service
        self._user_service = user_service

    async def execute(self, token: str | None) -> TokenClaims | None:
        if not token or not token.startswith("Bearer "):
            return None

        token = token.removeprefix("Bearer ")
        claims = await self._token_service.decode(token=token)
        if isinstance(claims, Err):  # pragma: no cover
            return None

        await self._user_service.sync_token_data(claims=claims.ok_value)

        return claims.ok_value
