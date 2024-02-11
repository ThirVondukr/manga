import aioinject
from passlib.context import CryptContext

from app.core.domain.auth.services import TokenService
from app.settings import AuthSettings
from lib.types import Providers


def _create_crypt_context(auth_settings: AuthSettings) -> CryptContext:
    return CryptContext(
        schemes=auth_settings.hashing_schemes,
    )


providers: Providers = [
    aioinject.Singleton(TokenService),
    aioinject.Singleton(_create_crypt_context),
]
