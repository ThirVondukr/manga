"""
Add bookmark count to manga

Revision ID: 419c7de3b33c
Revises: 35fa54397d0f
Create Date: 2024-03-17 07:10:17.018491

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "419c7de3b33c"
down_revision: str | None = "35fa54397d0f"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.add_column(
        "manga",
        sa.Column(
            "bookmark_count",
            sa.Integer(),
            server_default=sa.text("0"),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("manga", "bookmark_count")
