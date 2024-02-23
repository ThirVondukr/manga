import pytest
from faker import Faker

from tests.factories import ChapterFactory


@pytest.fixture
def chapter_factory(fake: Faker) -> ChapterFactory:
    return ChapterFactory(fake=fake)
