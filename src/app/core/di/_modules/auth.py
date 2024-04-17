import aioinject

from app.core.domain.auth.commands import (
    AuthenticateAccessTokenCommand,
)
from app.core.domain.auth.services import TokenService
from lib.types import Providers

providers: Providers = [
    aioinject.Singleton(TokenService),
    aioinject.Scoped(AuthenticateAccessTokenCommand),
]
