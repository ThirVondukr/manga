from aioinject import Scoped

from app.core.domain.branches.commands import MangaBranchCreateCommand
from app.core.domain.branches.services import MangaBranchService
from lib.types import Providers

providers: Providers = [
    Scoped(MangaBranchService),
    Scoped(MangaBranchCreateCommand),
]
