import pydantic
import pytest

from app.core.domain.const import GENERIC_NAME_LENGTH
from app.core.domain.groups.dto import GroupCreateDTO


def test_name() -> None:
    dto = GroupCreateDTO(name=" name ")
    assert dto.name == "name"

    with pytest.raises(pydantic.ValidationError):
        GroupCreateDTO(name="a" * (GENERIC_NAME_LENGTH + 1))
