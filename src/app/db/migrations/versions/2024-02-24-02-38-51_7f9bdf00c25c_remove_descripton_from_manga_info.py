"""
Remove descripton from manga info

Revision ID: 7f9bdf00c25c
Revises: cddc6a963387
Create Date: 2024-02-24 02:38:51.709703

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "7f9bdf00c25c"
down_revision: str | None = "cddc6a963387"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:

    op.drop_column("manga_info", "search_ts_vector")
    op.drop_column("manga_info", "description")
    op.add_column(
        "manga_info",
        sa.Column(
            "search_ts_vector",
            postgresql.TSVECTOR(),
            sa.Computed(
                "to_tsvector(language_regconfig, coalesce(title, ''))",
                persisted=True,
            ),
            nullable=False,
        ),
    )

    op.rename_table("manga_info", "manga_alt_title")
    op.drop_index("ix_manga_info_manga_id", table_name="manga_alt_title")
    op.create_index(
        op.f("ix_manga_alt_title_manga_id"),
        "manga_alt_title",
        ["manga_id"],
        unique=False,
    )
    op.create_index(
        "ix_manga_info_search_ts_vector",
        "manga_alt_title",
        ["search_ts_vector"],
        unique=False,
        postgresql_using="gin",
    )


def downgrade() -> None:
    op.drop_index(
        "ix_manga_info_search_ts_vector",
        table_name="manga_alt_title",
        postgresql_using="gin",
    )
    op.drop_index(
        op.f("ix_manga_alt_title_manga_id"),
        table_name="manga_alt_title",
    )
    op.create_index(
        "ix_manga_info_manga_id",
        "manga_alt_title",
        ["manga_id"],
        unique=False,
    )
    op.rename_table("manga_alt_title", "manga_info")
    op.add_column(
        "manga_info",
        sa.Column(
            "description",
            sa.VARCHAR(length=1000),
            autoincrement=False,
            nullable=False,
            server_default="",
        ),
    )
    op.alter_column("manga_info", "description", server_default=None)
    op.drop_column("manga_info", "search_ts_vector")
    op.add_column(
        "manga_info",
        sa.Column(
            "search_ts_vector",
            postgresql.TSVECTOR(),
            sa.Computed(
                "setweight(to_tsvector(language_regconfig, coalesce(title, '')), 'A') || setweight(to_tsvector(language_regconfig, coalesce(description, '')), 'D')",
                persisted=True,
            ),
            nullable=False,
        ),
    )
