from __future__ import annotations

from pathlib import PurePath
from uuid import UUID

from sqlalchemy import ARRAY, Column, ForeignKey, Integer, Table
from sqlalchemy.orm import (
    Mapped,
    MappedAsDataclass,
    mapped_column,
    relationship,
)

from app.db import Base
from app.db._base import PkUUID
from lib.tasks import TaskStatus

image_set__images = Table(
    "image_set__images",
    Base.metadata,
    Column(
        "image_set_id",
        ForeignKey("image_set.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "image_id",
        ForeignKey("image.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Image(PkUUID, MappedAsDataclass, Base, kw_only=True):
    __tablename__ = "image"

    path: Mapped[PurePath]
    width: Mapped[int]
    height: Mapped[int]


class ImageSet(PkUUID, MappedAsDataclass, Base, kw_only=True):
    __tablename__ = "image_set"

    original_id: Mapped[UUID] = mapped_column(
        ForeignKey("image.id"),
        init=False,
    )
    original: Mapped[Image] = relationship()
    images: Mapped[list[Image]] = relationship(
        secondary=image_set__images,
        default_factory=list,
    )


class ImageSetScaleTask(PkUUID, MappedAsDataclass, Base, kw_only=True):
    __tablename__ = "image_set_scale_task"

    image_set_id: Mapped[UUID] = mapped_column(
        ForeignKey("image_set.id"),
        init=False,
    )
    image_set: Mapped[ImageSet] = relationship()
    widths: Mapped[tuple[int, ...]] = mapped_column(
        ARRAY(item_type=Integer, as_tuple=True),
    )
    status: Mapped[TaskStatus]
