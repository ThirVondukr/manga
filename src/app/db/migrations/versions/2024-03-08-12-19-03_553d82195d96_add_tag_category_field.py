"""
Add tag category field

Revision ID: 553d82195d96
Revises: 386c64480ea5
Create Date: 2024-03-08 12:19:03.442071

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "553d82195d96"
down_revision: str | None = "386c64480ea5"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.add_column(
        "manga_tag",
        sa.Column(
            "category",
            sa.Enum("genre", "theme", name="tagcategory", native_enum=False),
            nullable=False,
        ),
    )
    op.execute("update manga_tag set category = 'theme';")
    op.alter_column("manga_tag", "category", nullable=False)


def downgrade() -> None:
    op.drop_column("manga_tag", "category")
