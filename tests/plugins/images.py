from collections.abc import Iterator

import aioinject
import pytest
from aioinject import Object

from app.core.storage import FileStorage
from tests.utils import TestFileStorage


@pytest.fixture
def image_storage(
    container: aioinject.Container,
) -> Iterator[FileStorage]:
    storage = TestFileStorage()
    with container.override(Object(storage, FileStorage)):
        yield storage
