from enum import IntEnum
from typing import TypeVar

from sqlalchemy import Dialect, Integer, TypeDecorator

TEnum = TypeVar("TEnum", bound=IntEnum)


class IntEnumType(TypeDecorator[TEnum]):
    impl = Integer

    def __init__(self, enum: type[TEnum]) -> None:
        super().__init__()
        self.enum = enum

    def process_bind_param(
        self,
        value: TEnum | None,
        dialect: Dialect,  # noqa: ARG002
    ) -> int | None:
        if value is None:
            return None
        return value.value

    def process_result_value(
        self,
        value: int | None,
        dialect: Dialect,  # noqa: ARG002
    ) -> TEnum | None:
        if value is None:
            return value
        return self.enum(value)
