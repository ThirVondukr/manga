"""
Create pgroonga extension

Revision ID: d49f687766a0
Revises: 7f9bdf00c25c
Create Date: 2024-02-24 21:54:10.518816

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "d49f687766a0"
down_revision: str | None = "7f9bdf00c25c"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.execute("create extension if not exists pgroonga;")


def downgrade() -> None:
    op.execute("drop extension pgroonga;")
