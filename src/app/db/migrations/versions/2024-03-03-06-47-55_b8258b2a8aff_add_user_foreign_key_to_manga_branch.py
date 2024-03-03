"""
Add user foreign key to manga branch

Revision ID: b8258b2a8aff
Revises: 84af585a609e
Create Date: 2024-03-03 06:47:55.617069

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "b8258b2a8aff"
down_revision: str | None = "84af585a609e"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.create_foreign_key(
        op.f("fk_manga_chapter_created_by_id_user"),
        "manga_chapter",
        "user",
        ["created_by_id"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint(
        op.f("fk_manga_chapter_created_by_id_user"),
        "manga_chapter",
        type_="foreignkey",
    )
