from collections.abc import Iterator

import aioinject
import pytest
from aioinject import Object

from app.core.domain.images.services import ImageService
from app.core.storage import FileStorage
from tests.types import Resolver
from tests.utils import TestFileStorage


@pytest.fixture
def image_storage(
    container: aioinject.Container,
) -> Iterator[FileStorage]:
    storage = TestFileStorage()
    with container.override(Object(storage, FileStorage)):
        yield storage


@pytest.fixture
async def image_service(resolver: Resolver) -> ImageService:
    return await resolver(ImageService)
