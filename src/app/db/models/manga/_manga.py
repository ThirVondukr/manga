from __future__ import annotations

from typing import TYPE_CHECKING, Final
from uuid import UUID

from sqlalchemy import (
    Double,
    ForeignKey,
    Index,
    literal,
)
from sqlalchemy.orm import (
    Mapped,
    MappedAsDataclass,
    mapped_column,
    relationship,
)

from app.db import Base
from app.db._base import (
    HasPrivate,
    HasTimestamps,
    PkUUID,
    str_title,
)
from lib.types import MangaStatus

from ._tags import manga_manga_tag_secondary_table

if TYPE_CHECKING:
    from app.db.models.manga import (
        AltTitle,
        MangaArt,
        MangaBranch,
        MangaChapter,
        MangaTag,
    )


class Manga(
    PkUUID,
    HasPrivate,
    HasTimestamps,
    MappedAsDataclass,
    Base,
    kw_only=True,
    repr=False,
):
    __tablename__ = "manga"
    __table_args__ = (
        Index(
            "ix_manga_title_pgroonga",
            "title",
            postgresql_using="pgroonga",
        ),
    )

    title: Mapped[str_title] = mapped_column(unique=True)
    title_slug: Mapped[str_title] = mapped_column(unique=True)
    description: Mapped[str]
    status: Mapped[MangaStatus]
    if TYPE_CHECKING:
        rating_count: Final[Mapped[int]] = mapped_column(default=0)
        rating: Final[Mapped[float]] = mapped_column(default=0.0)
        bookmark_count: Final[Mapped[int]] = mapped_column(default=0)
    else:
        rating_count: Mapped[int] = mapped_column(
            default=0,
            server_default=literal(0),
        )
        rating: Mapped[float] = mapped_column(
            Double,
            default=0.0,
            server_default=literal(0),
        )
        bookmark_count: Mapped[int] = mapped_column(
            default=0,
            server_default=literal(0),
        )

    latest_chapter_id: Mapped[UUID | None] = mapped_column(
        ForeignKey(
            "manga_chapter.id",
            ondelete="SET NULL",
            use_alter=True,
            initially="DEFERRED",
        ),
        default=None,
    )
    latest_chapter: Mapped[MangaChapter | None] = relationship(
        default=None,
        compare=False,
        lazy="raise",
    )

    branches: Mapped[list[MangaBranch]] = relationship(
        back_populates="manga",
        default_factory=list,
        compare=False,
        lazy="raise",
    )
    tags: Mapped[list[MangaTag]] = relationship(
        secondary=manga_manga_tag_secondary_table,
        back_populates="manga",
        default_factory=list,
        compare=False,
        lazy="raise",
    )
    alt_titles: Mapped[list[AltTitle]] = relationship(
        back_populates="manga",
        default_factory=list,
        compare=False,
        lazy="raise",
    )
    arts: Mapped[list[MangaArt]] = relationship(
        default_factory=list,
        back_populates="manga",
        order_by="MangaArt.volume",
        foreign_keys="MangaArt.manga_id",
    )
    cover_art_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("manga_art.id", use_alter=True, initially="DEFERRED"),
        init=False,
    )
    cover_art: Mapped[MangaArt | None] = relationship(
        default=None,
        foreign_keys=[cover_art_id],
    )
