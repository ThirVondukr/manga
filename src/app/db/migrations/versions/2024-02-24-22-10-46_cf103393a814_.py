"""
empty message

Revision ID: cf103393a814
Revises: d49f687766a0
Create Date: 2024-02-24 22:10:46.166577

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "cf103393a814"
down_revision: str | None = "d49f687766a0"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.drop_index(
        "ix_manga_info_search_ts_vector",
        table_name="manga_alt_title",
        postgresql_using="gin",
    )
    op.create_index(
        "ix_manga_info_title_pgroonga",
        "manga_alt_title",
        ["title"],
        unique=False,
        postgresql_using="pgroonga",
    )
    op.drop_column("manga_alt_title", "search_ts_vector")
    op.drop_column("manga_alt_title", "language_regconfig")


def downgrade() -> None:
    op.add_column(
        "manga_alt_title",
        sa.Column(
            "language_regconfig",
            sa.NullType(),
            autoincrement=False,
            nullable=False,
        ),
    )
    op.add_column(
        "manga_alt_title",
        sa.Column(
            "search_ts_vector",
            postgresql.TSVECTOR(),
            sa.Computed(
                "to_tsvector(language_regconfig, (COALESCE(title, ''::character varying))::text)",
                persisted=True,
            ),
            autoincrement=False,
            nullable=False,
        ),
    )
    op.drop_index(
        "ix_manga_info_title_pgroonga",
        table_name="manga_alt_title",
        postgresql_using="pgroonga",
    )
    op.create_index(
        "ix_manga_info_search_ts_vector",
        "manga_alt_title",
        ["search_ts_vector"],
        unique=False,
        postgresql_using="gin",
    )
