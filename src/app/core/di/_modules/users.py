from aioinject import Scoped

from app.core.domain.users.repositories import UserRepository
from app.core.domain.users.services import PermissionService
from lib.types import Providers

providers: Providers = [
    Scoped(PermissionService),
    Scoped(UserRepository),
]
