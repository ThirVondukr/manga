import uuid
from io import BytesIO
from pathlib import PurePath
from typing import Any

import pydantic
import pytest

from app.core.domain.chapters.dto import ChapterCreateDTO
from app.core.domain.const import NAME_LENGTH
from lib.files import InMemoryFile


@pytest.fixture
def kwargs() -> dict[str, Any]:
    return {
        "branch_id": uuid.uuid4(),
        "title": "Title",
        "volume": 1,
        "number": [1],
        "pages": [
            InMemoryFile(
                _buffer=BytesIO(),
                filename=PurePath("1.png"),
                content_type="image/png",
                size=0,
            ),
        ],
    }


def test_ok(kwargs: dict[str, Any]) -> None:
    dto = ChapterCreateDTO(
        **kwargs,
    )
    assert isinstance(dto, ChapterCreateDTO)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("title", " ab  "),
        ("title", "a" * (NAME_LENGTH + 1)),
        ("volume", 0),
        ("volume", -1),
        ("number", []),
        ("number", [-1]),
        ("number", [0]),
        ("number", [1, -1]),
        ("pages", []),
    ],
)
def test_validation_error(
    field: str,
    value: object,
    kwargs: dict[str, Any],
) -> None:
    kwargs[field] = value
    with pytest.raises(pydantic.ValidationError):
        ChapterCreateDTO(
            **kwargs,
        )
