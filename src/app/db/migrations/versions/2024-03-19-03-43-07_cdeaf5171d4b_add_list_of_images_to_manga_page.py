"""
Add list of images to manga page

Revision ID: cdeaf5171d4b
Revises: 01c61eb3cc08
Create Date: 2024-03-19 03:43:07.078138

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "cdeaf5171d4b"
down_revision: str | None = "01c61eb3cc08"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.create_table(
        "manga_page__image",
        sa.Column("manga_page_id", sa.Uuid(), nullable=False),
        sa.Column("image_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(
            ["image_id"],
            ["image.id"],
            name=op.f("fk_manga_page__image_image_id_image"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["manga_page_id"],
            ["manga_page.id"],
            name=op.f("fk_manga_page__image_manga_page_id_manga_page"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "manga_page_id",
            "image_id",
            name=op.f("pk_manga_page__image"),
        ),
    )


def downgrade() -> None:
    op.drop_table("manga_page__image")
