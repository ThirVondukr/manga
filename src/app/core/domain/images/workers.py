import logging
from contextlib import AsyncExitStack

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.domain.images.services import ImageService
from app.db.models import ImageSet, ImageSetScaleTask
from app.settings import ImageScaleSettings
from lib.tasks import TaskStatus


class ImageScaleTask:  # pragma: no cover
    def __init__(
        self,
        session: AsyncSession,
        image_service: ImageService,
        settings: ImageScaleSettings,
    ) -> None:
        self._session = session
        self._image_service = image_service
        self._settings = settings

    async def run_once(self) -> None:
        async with AsyncExitStack() as exit_stack:
            stmt = (
                select(ImageSetScaleTask)
                .with_for_update(skip_locked=True)
                .options(
                    selectinload(ImageSetScaleTask.image_set).selectinload(
                        ImageSet.images,
                    ),
                )
                .where(ImageSetScaleTask.status == TaskStatus.pending)
                .limit(self._settings.worker_batch_size)
            )
            for task in await self._session.scalars(stmt):
                logging.info(
                    "Processing image set %s, sizes %s",
                    task.image_set_id,
                    task.widths,
                )
                await self._image_service.scale_image_set(
                    image_set=task.image_set,
                    task=task,
                    exit_stack=exit_stack,
                )
                task.status = TaskStatus.done
                self._session.add(task)
            await self._session.flush()
