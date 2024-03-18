"""
Add manga rating

Revision ID: 01c61eb3cc08
Revises: 7d135886432d
Create Date: 2024-03-18 02:09:51.969379

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "01c61eb3cc08"
down_revision: str | None = "7d135886432d"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.create_table(
        "manga_rating",
        sa.Column("manga_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("rating", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "rating >= 1 and rating <= 10",
            name=op.f("ck_manga_rating_valid_rating_range_check"),
        ),
        sa.ForeignKeyConstraint(
            ["manga_id"],
            ["manga.id"],
            name=op.f("fk_manga_rating_manga_id_manga"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
            name=op.f("fk_manga_rating_user_id_user"),
        ),
        sa.PrimaryKeyConstraint(
            "manga_id",
            "user_id",
            name=op.f("pk_manga_rating"),
        ),
    )
    op.add_column(
        "manga",
        sa.Column(
            "rating_count",
            sa.Integer(),
            server_default=sa.text("0"),
            nullable=False,
        ),
    )
    op.add_column(
        "manga",
        sa.Column(
            "rating",
            sa.Double(),
            server_default=sa.text("0"),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("manga", "rating")
    op.drop_column("manga", "rating_count")
    op.drop_table("manga_rating")
