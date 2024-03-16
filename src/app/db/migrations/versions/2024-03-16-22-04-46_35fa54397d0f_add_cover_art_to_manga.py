"""
Add cover art to manga

Revision ID: 35fa54397d0f
Revises: c603db5b818e
Create Date: 2024-03-16 22:04:46.680234

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "35fa54397d0f"
down_revision: str | None = "c603db5b818e"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.add_column("manga", sa.Column("cover_art_id", sa.Uuid(), nullable=True))
    op.create_foreign_key(
        op.f("fk_manga_cover_art_id_manga_art"),
        "manga",
        "manga_art",
        ["cover_art_id"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint(
        op.f("fk_manga_cover_art_id_manga_art"),
        "manga",
        type_="foreignkey",
    )
    op.drop_column("manga", "cover_art_id")
