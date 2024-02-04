import functools
from typing import TYPE_CHECKING, TypeVar

import dotenv
from pydantic_settings import BaseSettings

TSettings = TypeVar("TSettings", bound=BaseSettings)


@functools.cache
def _load_dotenv_once() -> None:
    dotenv.load_dotenv()


def get_settings(cls: type[TSettings]) -> TSettings:
    _load_dotenv_once()
    return cls()


if not TYPE_CHECKING:  # Applying funtools.lru_cache returns Never
    get_settings = functools.lru_cache(get_settings)  # pragma: no cover
