import random

import pytest

from lib.types import Language


@pytest.fixture
def language() -> Language:
    return random.choice(list(Language.__members__.values()))
