import aioinject

from app.core.domain.users.commands import UserRegisterCommand
from app.core.domain.users.repositories import UserRepository
from lib.types import Providers

providers: Providers = [
    aioinject.Scoped(UserRepository),
    aioinject.Scoped(UserRegisterCommand),
]
