import aioinject

from app.core.domain.users.commands import UserRegisterCommand
from app.core.domain.users.repositories import UserRepository
from app.core.domain.users.services import UserService
from lib.types import Providers

providers: Providers = [
    aioinject.Scoped(UserRepository),
    aioinject.Scoped(UserService),
    aioinject.Scoped(UserRegisterCommand),
]
