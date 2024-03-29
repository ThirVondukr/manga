import collections
import functools
from collections.abc import Sequence
from typing import Annotated, Any, Protocol, TypeVar, runtime_checkable

from aioinject import Inject
from aioinject.ext.strawberry import inject
from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import QueryableAttribute
from sqlalchemy.sql.elements import SQLCoreOperations
from strawberry.dataloader import DataLoader

_K_contra = TypeVar("_K_contra", contravariant=True)
_V_co = TypeVar("_V_co", covariant=True)


@runtime_checkable
class LoaderProtocol(Protocol[_K_contra, _V_co]):
    async def execute(self, keys: Sequence[_K_contra]) -> Sequence[_V_co]: ...


class DataloaderProtocol(Protocol[_K_contra, _V_co]):
    async def __call__(self, keys: Sequence[_K_contra]) -> Sequence[_V_co]: ...


@functools.lru_cache
def map_dataloader_to_graphql(
    loader: type[LoaderProtocol[_K_contra, _V_co]],
) -> DataloaderProtocol[_K_contra, _V_co]:
    @inject
    async def inner(
        keys: Sequence[_K_contra],
        loader_instance: Annotated[loader, Inject],  # type: ignore[valid-type]
    ) -> Sequence[_V_co]:
        return await loader_instance.execute(  # type: ignore[no-any-return, attr-defined]
            keys=keys,
        )

    return inner  # type: ignore[return-value]


class Dataloaders:
    def __init__(self) -> None:
        self._loaders: dict[
            type[LoaderProtocol[Any, Any]],
            DataLoader[Any, Any],
        ] = {}

    def map(
        self,
        cls: type[LoaderProtocol[_K_contra, _V_co]],
    ) -> DataLoader[_K_contra, _V_co]:
        if cls not in self._loaders:  # pragma: no branch
            self._loaders[cls] = DataLoader(map_dataloader_to_graphql(cls))
        return self._loaders[cls]


K = TypeVar("K")
V = TypeVar("V")


class SQLALoader(LoaderProtocol[K, V | None], Protocol):
    column: QueryableAttribute[K]
    stmt: Select[tuple[V]]

    _session: AsyncSession

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def execute(self, keys: Sequence[K]) -> Sequence[V | None]:
        stmt = self.stmt.where(self.__class__.column.in_(keys))
        models = {
            getattr(model, self.__class__.column.key): model
            for model in await self._session.scalars(stmt)
        }
        return [models.get(key) for key in keys]


class SQLAListLoader(LoaderProtocol[K, Sequence[V]], Protocol):
    column: SQLCoreOperations[K]
    stmt: Select[tuple[K, V]]

    _session: AsyncSession

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def execute(self, keys: Sequence[K]) -> Sequence[Sequence[V]]:
        stmt = self.stmt.where(self.__class__.column.in_(keys))
        models = collections.defaultdict(list)
        for key, model in await self._session.execute(stmt):
            models[key].append(model)
        return [models[key] for key in keys]
