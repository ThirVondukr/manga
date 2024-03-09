"""
Add latest chapter id to manga

Revision ID: 904020f645f6
Revises: 553d82195d96
Create Date: 2024-03-09 20:08:31.421717

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "904020f645f6"
down_revision: str | None = "553d82195d96"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.add_column(
        "manga",
        sa.Column("latest_chapter_id", sa.Uuid(), nullable=True),
    )
    op.create_foreign_key(
        op.f("fk_manga_latest_chapter_id_manga_chapter"),
        "manga",
        "manga_chapter",
        ["latest_chapter_id"],
        ["id"],
        ondelete="SET NULL",
        initially="DEFERRED",
        use_alter=True,
    )
    op.execute(
        """
        update manga
            set latest_chapter_id = (
                select manga_chapter.id from manga_chapter
                join manga_branch mb on manga_chapter.branch_id = mb.id
                where mb.manga_id = manga.id
                order by manga_chapter.created_at desc
                limit 1
            )
        where 1 = 1;
        """,
    )


def downgrade() -> None:
    op.drop_constraint(
        op.f("fk_manga_latest_chapter_id_manga_chapter"),
        "manga",
        type_="foreignkey",
    )
    op.drop_column("manga", "latest_chapter_id")
