"""
Add group to manga branch

Revision ID: fd6f4d730746
Revises: b8258b2a8aff
Create Date: 2024-03-05 14:15:11.419738

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "fd6f4d730746"
down_revision: str | None = "b8258b2a8aff"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.add_column(
        "manga_branch",
        sa.Column("group_id", sa.Uuid(), nullable=False),
    )
    op.create_foreign_key(
        op.f("fk_manga_branch_group_id_group"),
        "manga_branch",
        "group",
        ["group_id"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint(
        op.f("fk_manga_branch_group_id_group"),
        "manga_branch",
        type_="foreignkey",
    )
    op.drop_column("manga_branch", "group_id")
