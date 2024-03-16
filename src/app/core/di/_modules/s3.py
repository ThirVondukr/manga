from aioinject import Singleton

from app.core.storage import FileStorage, S3FileStorage, create_s3
from lib.types import Providers

providers: Providers = [
    Singleton(create_s3),
    Singleton(S3FileStorage, type_=FileStorage),
]
