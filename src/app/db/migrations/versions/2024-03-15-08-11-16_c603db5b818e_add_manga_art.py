"""
Add manga art

Revision ID: c603db5b818e
Revises: 8b41c1c597c9
Create Date: 2024-03-15 08:11:16.416895

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "c603db5b818e"
down_revision: str | None = "8b41c1c597c9"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.create_table(
        "image",
        sa.Column("path", sa.String(), nullable=False),
        sa.Column(
            "dimensions",
            sa.ARRAY(sa.Integer(), as_tuple=True),
            nullable=False,
        ),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_image")),
    )
    op.create_table(
        "manga_art",
        sa.Column("volume", sa.Integer(), nullable=False),
        sa.Column(
            "language",
            sa.Enum("eng", "ukr", name="language", native_enum=False),
            nullable=False,
        ),
        sa.Column("manga_id", sa.Uuid(), nullable=False),
        sa.Column("image_id", sa.Uuid(), nullable=False),
        sa.Column("preview_image_id", sa.Uuid(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["image_id"],
            ["image.id"],
            name=op.f("fk_manga_art_image_id_image"),
        ),
        sa.ForeignKeyConstraint(
            ["manga_id"],
            ["manga.id"],
            name=op.f("fk_manga_art_manga_id_manga"),
        ),
        sa.ForeignKeyConstraint(
            ["preview_image_id"],
            ["image.id"],
            name=op.f("fk_manga_art_preview_image_id_image"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_manga_art")),
        sa.UniqueConstraint(
            "manga_id",
            "language",
            "volume",
            name="manga_art__manga_language_volume_uq",
        ),
    )


def downgrade() -> None:
    op.drop_table("manga_art")
    op.drop_table("image")
