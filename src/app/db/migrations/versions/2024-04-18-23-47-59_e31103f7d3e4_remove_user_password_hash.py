"""
Remove user password hash

Revision ID: e31103f7d3e4
Revises: 8b93deffb9f3
Create Date: 2024-04-18 23:47:59.138514

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "e31103f7d3e4"
down_revision: str | None = "8b93deffb9f3"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.drop_column("user", "password_hash")


def downgrade() -> None:
    op.add_column(
        "user",
        sa.Column(
            "password_hash",
            sa.VARCHAR(),
            autoincrement=False,
            nullable=False,
        ),
    )
