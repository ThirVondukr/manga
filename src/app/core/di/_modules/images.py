from aioinject import Scoped

from app.core.domain.images.loaders import ImageLoader
from app.core.domain.images.services import ImageService
from app.core.domain.images.workers import ImageScaleTask
from lib.types import Providers

providers: Providers = [
    Scoped(ImageService),
    Scoped(ImageLoader),
    Scoped(ImageScaleTask),
]
