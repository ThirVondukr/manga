"""
empty message

Revision ID: c1298bdd095b
Revises: 55e7f1a96737
Create Date: 2024-03-22 21:37:47.303051

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy import Integer

# revision identifiers, used by Alembic.
revision = "c1298bdd095b"
down_revision: str | None = "55e7f1a96737"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.add_column(
        "manga_bookmark",
        sa.Column("status", Integer, nullable=True),
    )
    op.execute(
        """
    update manga_bookmark set
    status = 1;
    """,
    )
    op.alter_column("manga_bookmark", "status", nullable=False)


def downgrade() -> None:
    op.drop_column("manga_bookmark", "status")
