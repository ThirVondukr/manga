"""
Add manga bookmark

Revision ID: 84af585a609e
Revises: 01aa09cf16f4
Create Date: 2024-02-29 23:28:26.295994

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "84af585a609e"
down_revision: str | None = "01aa09cf16f4"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.create_table(
        "manga_bookmark",
        sa.Column("manga_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["manga_id"],
            ["manga.id"],
            name=op.f("fk_manga_bookmark_manga_id_manga"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
            name=op.f("fk_manga_bookmark_user_id_user"),
        ),
        sa.PrimaryKeyConstraint(
            "manga_id",
            "user_id",
            name=op.f("pk_manga_bookmark"),
        ),
    )


def downgrade() -> None:
    op.drop_table("manga_bookmark")
