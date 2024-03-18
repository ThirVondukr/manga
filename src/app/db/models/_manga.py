from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime
from pathlib import PurePath
from typing import TYPE_CHECKING, Final
from uuid import UUID

from sqlalchemy import (
    ARRAY,
    CheckConstraint,
    Column,
    Double,
    ForeignKey,
    Index,
    Integer,
    String,
    Table,
    UniqueConstraint,
    literal,
)
from sqlalchemy.orm import (
    Mapped,
    MappedAsDataclass,
    mapped_column,
    relationship,
)

from app.core.domain.types import TagCategory
from app.db import Base
from app.db._base import (
    HasPrivate,
    HasTimestamps,
    PkUUID,
    str_title,
)
from lib.time import utc_now
from lib.types import Language, MangaStatus

if TYPE_CHECKING:
    from app.db.models import Group, User

manga_manga_tag_secondary_table = Table(
    "manga__manga_tag__secondary",
    Base.metadata,
    Column(
        "manga_id",
        ForeignKey("manga.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "tag_id",
        ForeignKey("manga_tag.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class MangaTag(PkUUID, MappedAsDataclass, Base, kw_only=True):
    __tablename__ = "manga_tag"

    name: Mapped[str] = mapped_column(String(32), unique=True)
    name_slug: Mapped[str] = mapped_column(String(32), unique=True)
    manga: Mapped[list[Manga]] = relationship(
        secondary=manga_manga_tag_secondary_table,
        back_populates="tags",
        default_factory=list,
        repr=False,
    )
    category: Mapped[TagCategory]


class MangaBookmark(MappedAsDataclass, Base, kw_only=True):
    __tablename__ = "manga_bookmark"

    manga_id: Mapped[UUID] = mapped_column(
        ForeignKey("manga.id"),
        primary_key=True,
        init=False,
    )
    manga: Mapped[Manga] = relationship(lazy="raise")
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("user.id"),
        primary_key=True,
        init=False,
    )
    user: Mapped[User] = relationship(lazy="raise")
    created_at: Mapped[datetime] = mapped_column(default_factory=utc_now)


class Image(PkUUID, MappedAsDataclass, Base, kw_only=True):
    __tablename__ = "image"

    path: Mapped[PurePath]
    dimensions: Mapped[tuple[int, int]] = mapped_column(
        ARRAY(Integer, as_tuple=True),
    )


class MangaArt(
    PkUUID,
    HasTimestamps,
    MappedAsDataclass,
    Base,
    kw_only=True,
    repr=False,
):
    __tablename__ = "manga_art"
    __table_args__ = (
        UniqueConstraint(
            "manga_id",
            "language",
            "volume",
            name="manga_art__manga_language_volume_uq",
        ),
    )

    volume: Mapped[int]
    language: Mapped[Language]

    manga_id: Mapped[UUID] = mapped_column(ForeignKey("manga.id"), init=False)
    manga: Mapped[Manga] = relationship(
        back_populates="arts",
        default=None,
        foreign_keys=[manga_id],
    )
    image_id: Mapped[UUID] = mapped_column(ForeignKey("image.id"), init=False)
    image: Mapped[Image] = relationship(foreign_keys=[image_id])
    preview_image_id: Mapped[UUID] = mapped_column(
        ForeignKey("image.id"),
        init=False,
    )
    preview_image: Mapped[Image] = relationship(foreign_keys=[preview_image_id])


class MangaRating(HasTimestamps, MappedAsDataclass, Base, kw_only=True):
    __tablename__ = "manga_rating"
    __table_args__ = (
        CheckConstraint(
            "rating >= 1 and rating <= 10",
            "valid_rating_range_check",
        ),
    )

    manga_id: Mapped[UUID] = mapped_column(
        ForeignKey("manga.id"),
        primary_key=True,
        init=False,
    )
    manga: Mapped[Manga] = relationship()
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("user.id"),
        primary_key=True,
        init=False,
    )
    user: Mapped[User] = relationship()
    rating: Mapped[int]


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


class MangaChapter(
    PkUUID,
    HasTimestamps,
    MappedAsDataclass,
    Base,
    kw_only=True,
):
    __tablename__ = "manga_chapter"
    __table_args__ = (
        UniqueConstraint(
            "branch_id",
            "number",
            name="manga_chapter__branch_number_uq",
        ),
    )

    branch_id: Mapped[UUID] = mapped_column(
        ForeignKey("manga_branch.id"),
        index=True,
        init=False,
    )
    branch: Mapped[MangaBranch] = relationship(back_populates="chapters")

    created_by_id: Mapped[UUID] = mapped_column(
        ForeignKey("user.id"),
        init=False,
    )
    created_by: Mapped[User] = relationship()

    title: Mapped[str] = mapped_column(String(250))

    volume: Mapped[int | None]
    number: Mapped[Sequence[int]] = mapped_column(ARRAY(Integer))

    pages: Mapped[list[MangaPage]] = relationship(
        order_by="MangaPage.number",
        back_populates="chapter",
    )


class MangaBranch(PkUUID, HasTimestamps, MappedAsDataclass, Base, kw_only=True):
    __tablename__ = "manga_branch"

    name: Mapped[str_title]
    manga_id: Mapped[UUID] = mapped_column(ForeignKey("manga.id"), init=False)
    manga: Mapped[Manga] = relationship(back_populates="branches")
    group_id: Mapped[UUID] = mapped_column(ForeignKey("group.id"), init=False)
    group: Mapped[Group] = relationship()

    language: Mapped[Language]

    chapters: Mapped[list[MangaChapter]] = relationship(
        back_populates="branch",
        default_factory=list,
        repr=False,
    )


class MangaPage(PkUUID, MappedAsDataclass, Base, kw_only=True):
    __tablename__ = "manga_page"
    __table_args__ = (UniqueConstraint("chapter_id", "number"),)

    chapter_id: Mapped[UUID] = mapped_column(
        ForeignKey("manga_chapter.id"),
        index=True,
        init=False,
    )
    chapter: Mapped[MangaChapter] = relationship(back_populates="pages")

    number: Mapped[int]
    image_path: Mapped[str] = mapped_column(String(250))


class AltTitle(
    PkUUID,
    HasTimestamps,
    MappedAsDataclass,
    Base,
    kw_only=True,
):
    __tablename__ = "manga_alt_title"
    __table_args__ = (
        Index(
            "ix_manga_alt_title_pgroonga",
            "title",
            postgresql_using="pgroonga",
        ),
    )

    manga_id: Mapped[UUID] = mapped_column(
        ForeignKey("manga.id"),
        index=True,
        default=None,
    )
    manga: Mapped[Manga] = relationship(
        back_populates="alt_titles",
        default=None,
    )
    language: Mapped[Language]
    title: Mapped[str] = mapped_column(String(250))
