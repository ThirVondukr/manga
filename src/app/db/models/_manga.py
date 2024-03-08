from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    ARRAY,
    Column,
    ForeignKey,
    Index,
    Integer,
    String,
    Table,
    UniqueConstraint,
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
    manga: Mapped[Manga] = relationship()
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("user.id"),
        primary_key=True,
        init=False,
    )
    user: Mapped[User] = relationship()
    created_at: Mapped[datetime] = mapped_column(default_factory=utc_now)


class Manga(
    PkUUID,
    HasPrivate,
    HasTimestamps,
    MappedAsDataclass,
    Base,
    kw_only=True,
):
    __tablename__ = "manga"

    title: Mapped[str_title] = mapped_column(unique=True)
    title_slug: Mapped[str_title] = mapped_column(unique=True)
    status: Mapped[MangaStatus]

    branches: Mapped[list[MangaBranch]] = relationship(
        back_populates="manga",
        default_factory=list,
    )
    tags: Mapped[list[MangaTag]] = relationship(
        secondary=manga_manga_tag_secondary_table,
        back_populates="manga",
        default_factory=list,
    )
    alt_titles: Mapped[list[AltTitle]] = relationship(
        back_populates="manga",
        default_factory=list,
    )


class MangaChapter(
    PkUUID,
    HasTimestamps,
    MappedAsDataclass,
    Base,
    kw_only=True,
):
    __tablename__ = "manga_chapter"

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
