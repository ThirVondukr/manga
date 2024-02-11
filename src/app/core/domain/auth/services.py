import jwt
from passlib.context import CryptContext
from result import Err, Ok, Result

from app.core.domain.auth.dto import (
    SignInDTO,
    TokenClaims,
    TokenWrapper,
    UserRegisterDTO,
)
from app.core.domain.users.errors import UserAlreadyExistsError
from app.core.domain.users.filters import UserFilter
from app.core.domain.users.repositories import UserRepository
from app.db.models import User
from app.settings import AuthSettings
from lib.db import DBContext
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


class AuthService:
    def __init__(
        self,
        repository: UserRepository,
        crypt_context: CryptContext,
        db_context: DBContext,
    ) -> None:
        self._repository = repository
        self._crypt_context = crypt_context
        self._db_context = db_context

    async def authenticate(self, dto: SignInDTO) -> User | None:
        user = await self._repository.get(filter=UserFilter(email=dto.email))
        if user is None:
            return None

        is_valid, new_hash = self._crypt_context.verify_and_update(
            secret=dto.password.get_secret_value(),
            hash=user.password_hash,
        )
        if not is_valid:
            return None

        if new_hash is not None:  # pragma: no cover
            user.password_hash = new_hash
            self._db_context.add(user)
            await self._db_context.flush()

        return user

    async def sign_up(
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
            password_hash=self._crypt_context.hash(
                dto.password.get_secret_value(),
            ),
        )
        self._db_context.add(user)
        await self._db_context.flush()
        return Ok(user)
