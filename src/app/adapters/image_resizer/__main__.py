import asyncio
import random

import aioinject

from app.core.di import create_container
from app.core.domain.images.workers import ImageScaleTask
from app.sentry import setup_logging
from app.settings import ImageScaleSettings
from lib.settings import get_settings


async def worker(
    settings: ImageScaleSettings,
    container: aioinject.Container,
) -> None:
    while True:
        async with container.context() as ctx:
            task = await ctx.resolve(ImageScaleTask)
            await task.run_once()

        await asyncio.sleep(
            settings.poll_interval
            + random.uniform(  # noqa: S311
                -settings.poll_jitter,
                settings.poll_jitter,
            ),
        )


async def main() -> None:
    setup_logging()
    settings = get_settings(ImageScaleSettings)
    async with (
        create_container() as container,
        asyncio.TaskGroup() as tg,
    ):
        for _ in range(settings.workers):
            tg.create_task(
                worker(container=container, settings=settings),
            )


asyncio.run(main())
