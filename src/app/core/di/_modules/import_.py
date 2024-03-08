from aioinject import Scoped

from app.core.domain.import_.cbz import ImportCBZCommand
from lib.types import Providers

providers: Providers = [
    Scoped(ImportCBZCommand),
]
