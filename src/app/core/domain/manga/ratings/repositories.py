from uuid import UUID

from sqlalchemy import func, literal, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.manga import Manga, MangaRating


class MangaRatingRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add_rating(
        self,
        manga: Manga,
        rating: float,
    ) -> None:
        stmt = (
            update(Manga)
            .where(Manga.id == manga.id)
            .values(
                rating_count=Manga.rating_count + literal(1),
                rating=Manga.rating
                / (Manga.rating_count + literal(1))
                * Manga.rating_count
                + rating / (Manga.rating_count + literal(1)),
            )
        )
        await self._session.execute(stmt)
        await self._session.refresh(manga, attribute_names=[Manga.rating.key])

    async def delete_rating(self, user_id: UUID, manga: Manga) -> None:
        rating_stmt = (
            select(MangaRating)
            .with_for_update()
            .where(
                MangaRating.manga_id == manga.id,
                MangaRating.user_id == user_id,
            )
        )
        existing_rating = await self._session.scalar(rating_stmt)
        if existing_rating is None:
            return  # pragma: no cover

        await self._session.delete(existing_rating)
        stmt = (
            update(Manga)
            .where(Manga.id == manga.id)
            .values(
                rating_count=Manga.rating_count - literal(1),
                rating=Manga.rating
                / func.greatest(Manga.rating_count - 1, 1)
                * Manga.rating_count
                - existing_rating.rating
                / func.greatest(Manga.rating_count - 1, 1),
            )
        )
        await self._session.execute(stmt)
        await self._session.refresh(manga, attribute_names=[Manga.rating.key])
