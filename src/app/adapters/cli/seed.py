import asyncio
import random

from sqlalchemy import delete
from tests.factories import MangaAltTitleFactory, MangaFactory, MangaTagFactory

from app.db import async_session_factory
from app.db.models.manga import AltTitle, Manga, MangaTag
from lib.types import Language


async def main() -> None:
    async with async_session_factory.begin() as session:
        for model in [AltTitle, MangaTag, Manga]:
            await session.execute(delete(model))

    async with async_session_factory.begin() as session:
        tags = MangaTagFactory.build_batch(size=20)
        session.add_all(tags)
        for _ in range(1):
            mangas = MangaFactory.build_batch(size=10_000)
            for manga in mangas:
                manga.tags = random.sample(
                    tags,
                    k=random.randint(1, 5),  # noqa: S311
                )
                manga.alt_titles = MangaAltTitleFactory.build_batch(
                    size=random.randint(1, 3),  # noqa: S311
                )
                manga.alt_titles.append(
                    AltTitle(title=manga.title, language=Language.eng),
                )

            session.add_all(mangas)
            await session.flush()


if __name__ == "__main__":
    asyncio.run(main())
