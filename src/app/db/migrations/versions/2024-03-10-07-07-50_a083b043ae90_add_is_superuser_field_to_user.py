"""
Add is_superuser field to user

Revision ID: a083b043ae90
Revises: 904020f645f6
Create Date: 2024-03-10 07:07:50.289745

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "a083b043ae90"
down_revision: str | None = "904020f645f6"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.add_column(
        "user",
        sa.Column(
            "is_superuser",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("user", "is_superuser")
