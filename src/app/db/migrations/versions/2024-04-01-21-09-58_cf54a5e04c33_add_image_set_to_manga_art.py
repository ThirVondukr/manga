"""
Add image set to manga art

Revision ID: cf54a5e04c33
Revises: d4d1e2a13dc6
Create Date: 2024-04-01 21:09:58.970531

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "cf54a5e04c33"
down_revision: str | None = "d4d1e2a13dc6"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.add_column(
        "manga_art",
        sa.Column("image_set_id", sa.Uuid(), nullable=True),
    )
    op.create_foreign_key(
        op.f("fk_manga_art_image_set_id_image_set"),
        "manga_art",
        "image_set",
        ["image_set_id"],
        ["id"],
    )
    op.execute(
        """
    insert into image_set (id, original_id)
    select
        manga_art.id,
        (
        select image.id from image
        join manga_art__image
            on image.id = manga_art__image.image_id
        where manga_art__image.manga_art_id = manga_art.id
        order by image.width desc
        limit 1
        ) as original_image_id
    from manga_art;
    """,
    )
    op.execute(
        """
    update manga_art
    set image_set_id = id;
    """,
    )
    op.execute(
        """
    insert into image_set__images (image_set_id, image_id)
    select manga_art_id, image_id from manga_art__image
    """,
    )

    op.alter_column("manga_art", "image_set_id", nullable=False)


def downgrade() -> None:
    op.drop_constraint(
        op.f("fk_manga_art_image_set_id_image_set"),
        "manga_art",
        type_="foreignkey",
    )
    op.drop_column("manga_art", "image_set_id")
