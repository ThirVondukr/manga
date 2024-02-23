import enum
import uuid
from datetime import datetime
from typing import Annotated

from sqlalchemy import DateTime, MetaData, String, func
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    MappedAsDataclass,
    mapped_column,
    registry,
)
from sqlalchemy.sql import expression
from uuid_utils.compat import uuid7

from lib.time import utc_now

meta = MetaData(
    naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    },
)


class PkUUID(MappedAsDataclass):
    # Would be better to use `Annotated` here,
    # but sqlalchemy does not support this
    id: Mapped[uuid.UUID] = mapped_column(
        default_factory=uuid7,
        primary_key=True,
    )


str_title = Annotated[str, mapped_column(String(250))]


class HasPrivate(MappedAsDataclass):
    is_public: Mapped[bool] = mapped_column(
        default=True,
        server_default=expression.true(),
    )


class HasTimestamps(MappedAsDataclass):
    created_at: Mapped[datetime] = mapped_column(
        default_factory=utc_now,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        default_factory=utc_now,
        server_default=func.now(),
        server_onupdate=func.now(),  # type: ignore[arg-type]
    )


class RegConfigLanguage(enum.Enum):
    eng = "english"
    ukr = "ukrainian"


class Base(DeclarativeBase):
    metadata = meta

    registry = registry(
        type_annotation_map={
            datetime: DateTime(timezone=True),
            # enum.Enum: Enum(native_enum=False),
        },
    )
