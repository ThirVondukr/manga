"""
Use separate columns for image dimensions

Revision ID: e0d15cea1b71
Revises: fc8c45ddde5b
Create Date: 2024-03-19 04:14:57.666578

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "e0d15cea1b71"
down_revision: str | None = "fc8c45ddde5b"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.add_column("image", sa.Column("width", sa.Integer(), nullable=True))
    op.add_column("image", sa.Column("height", sa.Integer(), nullable=True))
    op.execute(
        """
    update image
    set width = dimensions[1],
        height = dimensions[2]
    """,
    )

    op.alter_column("image", "width", nullable=False)
    op.alter_column("image", "height", nullable=False)
    op.drop_column("image", "dimensions")


def downgrade() -> None:
    op.add_column(
        "image",
        sa.Column(
            "dimensions",
            postgresql.ARRAY(sa.INTEGER()),
            autoincrement=False,
            nullable=False,
        ),
    )
    op.drop_column("image", "height")
    op.drop_column("image", "width")
