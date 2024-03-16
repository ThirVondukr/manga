from enum import IntEnum
from pathlib import PurePath
from typing import TypeVar

from sqlalchemy import Dialect, Integer, String, TypeDecorator

TEnum = TypeVar("TEnum", bound=IntEnum)


class IntEnumType(TypeDecorator[TEnum]):
    impl = Integer
    cache_ok = True

    def __init__(self, enum: type[TEnum]) -> None:
        super().__init__()
        self.enum = enum

    def process_bind_param(
        self,
        value: TEnum | None,
        dialect: Dialect,  # noqa: ARG002
    ) -> int | None:
        if value is None:  # pragma: no cover
            return None
        return value.value

    def process_result_value(
        self,
        value: int | None,
        dialect: Dialect,  # noqa: ARG002
    ) -> TEnum | None:
        if value is None:  # pragma: no cover
            return value
        return self.enum(value)


class PurePathType(TypeDecorator[PurePath]):
    impl = String

    def process_bind_param(
        self,
        value: PurePath | str | None,
        dialect: Dialect,  # noqa: ARG002
    ) -> str | None:
        if value is None:  # pragma: no cover
            return None
        if isinstance(value, str):
            value = PurePath(value)
        return value.as_posix()

    def process_result_value(
        self,
        value: str | None,
        dialect: Dialect,  # noqa: ARG002
    ) -> PurePath | None:
        if value is None:  # pragma: no cover
            return None
        return PurePath(value)
