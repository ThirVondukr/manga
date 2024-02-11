import jwt

from app.core.domain.auth.dto import TokenClaims, TokenWrapper
from app.db.models import User
from app.settings import AuthSettings
from lib.time import utc_now


class TokenService:
    def __init__(self, settings: AuthSettings) -> None:
        self._settings = settings

    def create_access_token(self, user: User) -> TokenWrapper:
        now = utc_now()
        access = TokenClaims(
            token_type="access",  # noqa: S106
            sub=user.id,
            exp=now + self._settings.access_token_lifetime,
            iat=now,
        )
        return self._encode(claims=access)

    def create_refresh_token(self, user: User) -> TokenWrapper:
        now = utc_now()
        access = TokenClaims(
            token_type="refresh",  # noqa: S106
            sub=user.id,
            exp=now + self._settings.refresh_token_lifetime,
            iat=now,
        )
        return self._encode(claims=access)

    def decode(self, token: str) -> TokenClaims:
        claims = jwt.decode(
            jwt=token,
            key=self._settings.public_key,
            algorithms=[self._settings.algorithm],
        )
        return TokenClaims.model_validate(claims)

    def _encode(self, claims: TokenClaims) -> TokenWrapper:
        return TokenWrapper(
            claims=claims,
            token=jwt.encode(
                payload=claims.model_dump(mode="json"),
                key=self._settings.private_key,
                algorithm=self._settings.algorithm,
            ),
        )
