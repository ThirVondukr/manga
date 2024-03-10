"""
Add pgroonga index to Manga.title

Revision ID: d9971d6b3533
Revises: 59330ec76ad5
Create Date: 2024-03-10 17:32:15.223286

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "d9971d6b3533"
down_revision: str | None = "59330ec76ad5"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.create_index(
        "ix_manga_title_pgroonga",
        "manga",
        ["title"],
        unique=False,
        postgresql_using="pgroonga",
    )


def downgrade() -> None:
    op.drop_index(
        "ix_manga_title_pgroonga",
        table_name="manga",
        postgresql_using="pgroonga",
    )
