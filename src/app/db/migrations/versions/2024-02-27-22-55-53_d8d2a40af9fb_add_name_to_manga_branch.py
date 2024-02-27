"""
Add name to manga branch

Revision ID: d8d2a40af9fb
Revises: 1a2aacea6298
Create Date: 2024-02-27 22:55:53.126257

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "d8d2a40af9fb"
down_revision: str | None = "1a2aacea6298"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.add_column(
        "manga_branch",
        sa.Column("name", sa.String(length=250), nullable=True),
    )
    op.execute("update manga_branch set name = '';")
    op.alter_column("manga_branch", "name", nullable=False)


def downgrade() -> None:
    op.drop_column("manga_branch", "name")
