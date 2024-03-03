from aioinject import Singleton

from app.core.storage import ImageStorage, S3ImageStorage, create_s3
from lib.types import Providers

providers: Providers = [
    Singleton(create_s3),
    Singleton(S3ImageStorage, type_=ImageStorage),
]
