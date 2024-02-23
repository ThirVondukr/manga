from __future__ import annotations

from uuid import UUID

from sqlalchemy import (
    Column,
    Computed,
    ForeignKey,
    Index,
    String,
    Table,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import REGCONFIG, TSVECTOR
from sqlalchemy.engine.default import DefaultExecutionContext
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
    RegConfigLanguage,
    str_title,
)
from lib.types import Language

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

    branches: Mapped[list[MangaBranch]] = relationship(
        back_populates="manga",
        default_factory=list,
    )
    tags: Mapped[list[MangaTag]] = relationship(
        secondary=manga_manga_tag_secondary_table,
        back_populates="manga",
        default_factory=list,
    )
    info: Mapped[list[MangaInfo]] = relationship(
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
    )
    branch: Mapped[MangaBranch] = relationship(back_populates="chapters")

    created_by_id: Mapped[UUID]
    title: Mapped[str] = mapped_column(String(250))

    volume: Mapped[int | None]
    number: Mapped[str] = mapped_column(String(40))

    pages: Mapped[list[MangaPage]] = relationship(
        order_by="MangaPage.number",
        back_populates="chapter",
    )


class MangaBranch(PkUUID, HasTimestamps, MappedAsDataclass, Base, kw_only=True):
    __tablename__ = "manga_branch"

    manga_id: Mapped[UUID] = mapped_column(ForeignKey("manga.id"))
    manga: Mapped[Manga] = relationship(back_populates="branches")

    language: Mapped[Language]

    chapters: Mapped[MangaChapter] = relationship(back_populates="branch")


class MangaPage(PkUUID, MappedAsDataclass, Base, kw_only=True):
    __tablename__ = "manga_page"
    __table_args__ = (UniqueConstraint("chapter_id", "number"),)

    chapter_id: Mapped[UUID] = mapped_column(
        ForeignKey("manga_chapter.id"),
        index=True,
    )
    chapter: Mapped[MangaChapter] = relationship(back_populates="pages")

    number: Mapped[int]
    image_path: Mapped[str] = mapped_column(String(250))


def _regconfig_default(ctx: DefaultExecutionContext) -> str:
    return RegConfigLanguage[ctx.current_parameters["language"].value].value  # type: ignore[index]


class MangaInfo(
    PkUUID,
    HasTimestamps,
    MappedAsDataclass,
    Base,
    kw_only=True,
):
    __tablename__ = "manga_info"
    __table_args__ = (
        Index(
            "ix_manga_info_search_ts_vector",
            "search_ts_vector",
            postgresql_using="gin",
        ),
    )

    manga_id: Mapped[UUID] = mapped_column(ForeignKey("manga.id"), index=True)
    manga: Mapped[Manga] = relationship(back_populates="info")
    language: Mapped[Language]
    language_regconfig: Mapped[str] = mapped_column(
        REGCONFIG,
        insert_default=_regconfig_default,
    )
    title: Mapped[str] = mapped_column(String(250))
    description: Mapped[str] = mapped_column(
        String(1000),
        nullable=False,
    )
    search_ts_vector: Mapped[str] = mapped_column(
        TSVECTOR,
        Computed(
            "setweight(to_tsvector(language_regconfig, coalesce(title, '')), 'A') || "
            "setweight(to_tsvector(language_regconfig, coalesce(description, '')), 'D')",
            persisted=True,
        ),
    )
