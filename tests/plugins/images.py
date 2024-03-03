from collections.abc import Iterator

import aioinject
import pytest
from aioinject import Object

from app.core.storage import ImageStorage
from tests.utils import TestImageStorage


@pytest.fixture
def image_storage(
    container: aioinject.Container,
) -> Iterator[ImageStorage]:
    storage = TestImageStorage()
    with container.override(Object(storage, ImageStorage)):
        yield storage
