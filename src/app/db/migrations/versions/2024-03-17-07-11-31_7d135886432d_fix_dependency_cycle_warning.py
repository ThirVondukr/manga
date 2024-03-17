"""
Fix dependency cycle warning

Revision ID: 7d135886432d
Revises: 419c7de3b33c
Create Date: 2024-03-17 07:11:31.702469

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "7d135886432d"
down_revision: str | None = "419c7de3b33c"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.drop_constraint(
        "fk_manga_cover_art_id_manga_art",
        "manga",
        type_="foreignkey",
    )
    op.create_foreign_key(
        op.f("fk_manga_cover_art_id_manga_art"),
        "manga",
        "manga_art",
        ["cover_art_id"],
        ["id"],
        initially="DEFERRED",
        use_alter=True,
    )


def downgrade() -> None:
    op.drop_constraint(
        op.f("fk_manga_cover_art_id_manga_art"),
        "manga",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "fk_manga_cover_art_id_manga_art",
        "manga",
        "manga_art",
        ["cover_art_id"],
        ["id"],
    )
