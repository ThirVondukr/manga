"""
Make chapter number unique per branch

Revision ID: 59330ec76ad5
Revises: a083b043ae90
Create Date: 2024-03-10 07:26:35.252787

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "59330ec76ad5"
down_revision: str | None = "a083b043ae90"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.create_unique_constraint(
        "manga_chapter__branch_number_uq",
        "manga_chapter",
        ["branch_id", "number"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "manga_chapter__branch_number_uq",
        "manga_chapter",
        type_="unique",
    )
