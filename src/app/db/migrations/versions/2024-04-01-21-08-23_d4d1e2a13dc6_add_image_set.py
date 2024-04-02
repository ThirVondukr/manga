"""
Add image set

Revision ID: d4d1e2a13dc6
Revises: c1298bdd095b
Create Date: 2024-04-01 21:08:23.088401

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "d4d1e2a13dc6"
down_revision: str | None = "c1298bdd095b"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.create_table(
        "image_set",
        sa.Column("original_id", sa.Uuid(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(
            ["original_id"],
            ["image.id"],
            name=op.f("fk_image_set_original_id_image"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_image_set")),
    )
    op.create_table(
        "image_set__images",
        sa.Column("image_set_id", sa.Uuid(), nullable=False),
        sa.Column("image_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(
            ["image_id"],
            ["image.id"],
            name=op.f("fk_image_set__images_image_id_image"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["image_set_id"],
            ["image_set.id"],
            name=op.f("fk_image_set__images_image_set_id_image_set"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "image_set_id",
            "image_id",
            name=op.f("pk_image_set__images"),
        ),
    )


def downgrade() -> None:
    op.drop_table("image_set__images")
    op.drop_table("image_set")
