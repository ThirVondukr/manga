from datetime import datetime
from typing import TYPE_CHECKING, Annotated, Self
from uuid import UUID

import strawberry
from strawberry import Private

from app.adapters.graphql.context import Info
from app.adapters.graphql.dto import DTOMixin
from app.adapters.graphql.types import (
    MangaBookmarkStatusGQL,
)
from app.core.domain.manga.manga.loaders import (
    MangaLoader,
)
from app.db.models.manga import (
    MangaBookmark,
)

if TYPE_CHECKING:
    from app.adapters.graphql.apps.manga.types import MangaGQL


@strawberry.type(name="MangaBookmark")
class MangaBookmarkGQL(DTOMixin[MangaBookmark]):
    _manga_id: Private[UUID]
    id: strawberry.ID
    status: MangaBookmarkStatusGQL
    created_at: datetime

    @classmethod
    def from_dto(cls, model: MangaBookmark) -> Self:
        return cls(
            _manga_id=model.manga_id,
            id=strawberry.ID(f"{model.user_id}:{model.manga_id}"),
            status=model.status,
            created_at=model.created_at,
        )

    @strawberry.field
    async def manga(
        self,
        info: Info,
    ) -> Annotated[
        "MangaGQL",
        strawberry.lazy("app.adapters.graphql.apps.manga.types"),
    ]:
        from app.adapters.graphql.apps.manga.types import MangaGQL

        manga = await info.context.loaders.map(MangaLoader).load(self._manga_id)
        if not manga:
            raise ValueError  # pragma: no cover
        return MangaGQL.from_dto(manga)
