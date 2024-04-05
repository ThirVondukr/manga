"""
empty message

Revision ID: 8b93deffb9f3
Revises: 7620bed5acf2
Create Date: 2024-04-05 17:10:31.628533

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "8b93deffb9f3"
down_revision: str | None = "7620bed5acf2"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.drop_constraint(
        "fk_image_set_scale_task_image_set_id_image_set",
        "image_set_scale_task",
        type_="foreignkey",
    )
    op.create_foreign_key(
        op.f("fk_image_set_scale_task_image_set_id_image_set"),
        "image_set_scale_task",
        "image_set",
        ["image_set_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    op.drop_constraint(
        op.f("fk_image_set_scale_task_image_set_id_image_set"),
        "image_set_scale_task",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "fk_image_set_scale_task_image_set_id_image_set",
        "image_set_scale_task",
        "image_set",
        ["image_set_id"],
        ["id"],
    )
