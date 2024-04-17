import jwt
from jwt import PyJWTError
from result import Err, Ok, Result

from app.core.domain.auth.dto import (
    TokenClaims,
)
from app.core.domain.auth.errors import TokenDecodeError
from app.settings import AuthSettings, KeycloakSettings
from lib.connectors.keycloak import KeycloakClient


class TokenService:
    def __init__(
        self,
        settings: AuthSettings,
        keycloak_client: KeycloakClient,
        keycloak_settings: KeycloakSettings,
    ) -> None:
        self._settings = settings
        self._keycloak_client = keycloak_client
        self._keycloak_settings = keycloak_settings

    async def decode(self, token: str) -> Result[TokenClaims, TokenDecodeError]:
        realm = await self._keycloak_client.realm_info(
            realm=self._keycloak_settings.realm,
        )
        if realm is None:
            raise ValueError  # pragma: no cover

        try:
            claims = jwt.decode(
                jwt=token,
                key=self._settings.public_key_begin
                + realm.public_key
                + self._settings.public_key_end,
                algorithms=[self._settings.algorithm],
                audience=self._settings.audience,
            )
        except PyJWTError as error:  # pragma: no cover
            return Err(TokenDecodeError(error=error))
        return Ok(TokenClaims.model_validate(claims))
