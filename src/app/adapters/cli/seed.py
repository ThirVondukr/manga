import asyncio
import random

from sqlalchemy import delete
from tests.factories import MangaFactory, MangaTagFactory

from app.db import async_session_factory
from app.db.models import Manga, MangaTag


async def main() -> None:
    async with async_session_factory.begin() as session:
        for model in [MangaTag, Manga]:
            await session.execute(delete(model))

    async with async_session_factory.begin() as session:
        tags = MangaTagFactory.build_batch(size=20)
        session.add_all(tags)
        mangas = MangaFactory.build_batch(size=1000)
        for manga in mangas:
            manga.tags = random.sample(
                tags,
                k=random.randint(1, 5),  # noqa: S311
            )

        session.add_all(mangas)
        await session.flush()


if __name__ == "__main__":
    asyncio.run(main())
