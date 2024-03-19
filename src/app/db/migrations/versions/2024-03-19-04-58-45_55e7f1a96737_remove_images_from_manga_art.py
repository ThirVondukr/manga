"""
Remove images from manga art

Revision ID: 55e7f1a96737
Revises: 573c99f9f3b9
Create Date: 2024-03-19 04:58:45.636173

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "55e7f1a96737"
down_revision: str | None = "573c99f9f3b9"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.drop_constraint(
        "fk_manga_art_preview_image_id_image",
        "manga_art",
        type_="foreignkey",
    )
    op.drop_constraint(
        "fk_manga_art_image_id_image",
        "manga_art",
        type_="foreignkey",
    )
    op.drop_column("manga_art", "preview_image_id")
    op.drop_column("manga_art", "image_id")


def downgrade() -> None:
    op.add_column(
        "manga_art",
        sa.Column("image_id", sa.UUID(), autoincrement=False, nullable=False),
    )
    op.add_column(
        "manga_art",
        sa.Column(
            "preview_image_id",
            sa.UUID(),
            autoincrement=False,
            nullable=False,
        ),
    )
    op.create_foreign_key(
        "fk_manga_art_image_id_image",
        "manga_art",
        "image",
        ["image_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_manga_art_preview_image_id_image",
        "manga_art",
        "image",
        ["preview_image_id"],
        ["id"],
    )
