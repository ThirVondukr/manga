"""
Use array for manga chapter number

Revision ID: 386c64480ea5
Revises: fd6f4d730746
Create Date: 2024-03-06 13:29:01.195341

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "386c64480ea5"
down_revision: str | None = "fd6f4d730746"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.alter_column(
        "manga_chapter",
        "number",
        existing_type=sa.VARCHAR(length=40),
        type_=sa.ARRAY(sa.Integer()),
        existing_nullable=False,
        postgresql_using="number::integer[]",
    )


def downgrade() -> None:
    op.alter_column(
        "manga_chapter",
        "number",
        existing_type=sa.ARRAY(sa.Integer()),
        type_=sa.VARCHAR(length=40),
        existing_nullable=False,
    )
