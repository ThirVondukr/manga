from aioinject import Scoped

from app.core.domain.groups.commands import GroupCreateCommand
from app.core.domain.groups.repositories import GroupRepository
from app.core.domain.groups.services import GroupService
from lib.types import Providers

providers: Providers = [
    Scoped(GroupRepository),
    Scoped(GroupService),
    Scoped(GroupCreateCommand),
]
