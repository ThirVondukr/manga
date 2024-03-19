"""
Add images to manga art

Revision ID: 573c99f9f3b9
Revises: e0d15cea1b71
Create Date: 2024-03-19 04:53:49.143193

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "573c99f9f3b9"
down_revision: str | None = "e0d15cea1b71"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.create_table(
        "manga_art__image",
        sa.Column("manga_art_id", sa.Uuid(), nullable=False),
        sa.Column("image_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(
            ["image_id"],
            ["image.id"],
            name=op.f("fk_manga_art__image_image_id_image"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["manga_art_id"],
            ["manga_art.id"],
            name=op.f("fk_manga_art__image_manga_art_id_manga_art"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "manga_art_id",
            "image_id",
            name=op.f("pk_manga_art__image"),
        ),
    )

    op.execute(
        """
        insert into manga_art__image (image_id, manga_art_id)
        select image_id, id from manga_art;
        """,
    )
    op.execute(
        """
        insert into manga_art__image (image_id, manga_art_id)
        select preview_image_id, id from manga_art;
        """,
    )


def downgrade() -> None:
    op.drop_table("manga_art__image")
