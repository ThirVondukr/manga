"""
Add image scale task

Revision ID: 7620bed5acf2
Revises: cf54a5e04c33
Create Date: 2024-04-02 10:09:12.245750

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "7620bed5acf2"
down_revision: str | None = "cf54a5e04c33"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.create_table(
        "image_set_scale_task",
        sa.Column("image_set_id", sa.Uuid(), nullable=False),
        sa.Column(
            "widths",
            sa.ARRAY(sa.Integer(), as_tuple=True),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum(
                "pending",
                "done",
                "error",
                name="taskstatus",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(
            ["image_set_id"],
            ["image_set.id"],
            name=op.f("fk_image_set_scale_task_image_set_id_image_set"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_image_set_scale_task")),
    )


def downgrade() -> None:
    op.drop_table("image_set_scale_task")
