"""
Remove manga_page.image_path

Revision ID: fc8c45ddde5b
Revises: cdeaf5171d4b
Create Date: 2024-03-19 04:11:55.436174

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "fc8c45ddde5b"
down_revision: str | None = "cdeaf5171d4b"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.drop_column("manga_page", "image_path")


def downgrade() -> None:
    op.add_column(
        "manga_page",
        sa.Column(
            "image_path",
            sa.VARCHAR(length=250),
            autoincrement=False,
            nullable=False,
        ),
    )
