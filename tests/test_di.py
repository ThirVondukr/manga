from aioinject import validation

from app.core.di import create_container


def test_validate_container() -> None:
    container = create_container()
    validation.validate_container(container, validation.DEFAULT_VALIDATORS)
