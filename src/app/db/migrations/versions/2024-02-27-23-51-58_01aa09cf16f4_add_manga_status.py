"""
Add manga status

Revision ID: 01aa09cf16f4
Revises: d8d2a40af9fb
Create Date: 2024-02-27 23:51:58.269706

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy import Integer

# revision identifiers, used by Alembic.
revision = "01aa09cf16f4"
down_revision: str | None = "d8d2a40af9fb"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.add_column(
        "manga",
        sa.Column("status", Integer, nullable=True),
    )
    op.execute("update manga set status = 0;")
    op.alter_column("manga", "status", nullable=False)


def downgrade() -> None:
    op.drop_column("manga", "status")
