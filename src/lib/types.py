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
    ukr = "ukr"


class MangaStatus(enum.IntEnum):
    ongoing = 0
    completed = enum.auto()
    cancelled = enum.auto()
    on_hold = enum.auto()


class Unset(enum.Enum):
    unset = enum.auto()
