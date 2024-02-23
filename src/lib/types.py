import enum
from collections.abc import Iterable
from datetime import datetime
from typing import Annotated, Any, TypeAlias

from aioinject import Provider
from pydantic import PlainSerializer

Providers: TypeAlias = Iterable[Provider[Any]]

DatetimeInt = Annotated[datetime, PlainSerializer(lambda t: int(t.timestamp()))]


class Language(enum.Enum):
    eng = "eng"
    rus = "rus"
    ukr = "ukr"
