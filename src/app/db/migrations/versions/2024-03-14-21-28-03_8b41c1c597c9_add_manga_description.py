"""
Add manga description

Revision ID: 8b41c1c597c9
Revises: d9971d6b3533
Create Date: 2024-03-14 21:28:03.596125

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "8b41c1c597c9"
down_revision: str | None = "d9971d6b3533"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.add_column(
        "manga",
        sa.Column("description", sa.String(), nullable=True),
    )
    op.execute("update manga set description = '';")
    op.alter_column("manga", "description", nullable=False)


def downgrade() -> None:
    op.drop_column("manga", "description")
