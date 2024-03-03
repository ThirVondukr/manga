from collections.abc import Iterable, Sequence
from typing import Protocol, TypeVar, runtime_checkable

from sqlalchemy.orm import DeclarativeBase

T = TypeVar("T", bound=DeclarativeBase)


@runtime_checkable
class DBContext(Protocol):
    """
    Constrained interface for sqlalchemy AsyncSession.

    It's meant to be used in services or commands to persist data
    without having to reach out for AsyncSession directly.
    """

    def add(self, instance: T) -> None: ...

    def add_all(self, instances: Iterable[T]) -> None: ...

    async def flush(self, objects: Sequence[T] | None = ...) -> None: ...
