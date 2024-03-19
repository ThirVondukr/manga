from collections.abc import Sequence
from typing import NamedTuple
from uuid import UUID

from sqlalchemy import select, tuple_
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.manga import MangaBookmark
from lib.loaders import LoaderProtocol


class MangaBookmarkLoaderKey(NamedTuple):
    manga_id: UUID
    user_id: UUID


class MangaBookmarkLoader(
    LoaderProtocol[MangaBookmarkLoaderKey, MangaBookmark | None],
):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def execute(
        self,
        keys: Sequence[MangaBookmarkLoaderKey],
    ) -> Sequence[MangaBookmark | None]:
        stmt = select(MangaBookmark).where(
            tuple_(MangaBookmark.manga_id, MangaBookmark.user_id).in_(keys),
        )

        result = {
            (bookmark.manga_id, bookmark.user_id): bookmark
            for bookmark in await self._session.scalars(stmt)
        }

        return [result.get(key) for key in keys]
