"""
Initial

Revision ID: 1a2aacea6298
Revises:
Create Date: 2024-02-25 23:59:02.552012

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "1a2aacea6298"
down_revision: str | None = None
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.execute("create extension if not exists pgroonga;")
    op.create_table(
        "manga",
        sa.Column("title", sa.String(length=250), nullable=False),
        sa.Column("title_slug", sa.String(length=250), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "is_public",
            sa.Boolean(),
            server_default=sa.text("true"),
            nullable=False,
        ),
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
        sa.PrimaryKeyConstraint("id", name=op.f("pk_manga")),
        sa.UniqueConstraint("title", name=op.f("uq_manga_title")),
        sa.UniqueConstraint("title_slug", name=op.f("uq_manga_title_slug")),
    )
    op.create_table(
        "manga_tag",
        sa.Column("name", sa.String(length=32), nullable=False),
        sa.Column("name_slug", sa.String(length=32), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_manga_tag")),
        sa.UniqueConstraint("name", name=op.f("uq_manga_tag_name")),
        sa.UniqueConstraint("name_slug", name=op.f("uq_manga_tag_name_slug")),
    )
    op.create_table(
        "user",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("username", sa.String(length=40), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_user")),
        sa.UniqueConstraint("email", name=op.f("uq_user_email")),
        sa.UniqueConstraint("username", name=op.f("uq_user_username")),
    )
    op.create_table(
        "group",
        sa.Column("name", sa.String(length=250), nullable=False),
        sa.Column("created_by_id", sa.Uuid(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
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
        sa.ForeignKeyConstraint(
            ["created_by_id"],
            ["user.id"],
            name=op.f("fk_group_created_by_id_user"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_group")),
    )
    op.create_table(
        "manga__manga_tag__secondary",
        sa.Column("manga_id", sa.Uuid(), nullable=False),
        sa.Column("tag_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(
            ["manga_id"],
            ["manga.id"],
            name=op.f("fk_manga__manga_tag__secondary_manga_id_manga"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["tag_id"],
            ["manga_tag.id"],
            name=op.f("fk_manga__manga_tag__secondary_tag_id_manga_tag"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "manga_id",
            "tag_id",
            name=op.f("pk_manga__manga_tag__secondary"),
        ),
    )
    op.create_table(
        "manga_alt_title",
        sa.Column("manga_id", sa.Uuid(), nullable=False),
        sa.Column(
            "language",
            sa.Enum("eng", "ukr", name="language"),
            nullable=False,
        ),
        sa.Column("title", sa.String(length=250), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
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
        sa.ForeignKeyConstraint(
            ["manga_id"],
            ["manga.id"],
            name=op.f("fk_manga_alt_title_manga_id_manga"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_manga_alt_title")),
    )
    op.create_index(
        op.f("ix_manga_alt_title_manga_id"),
        "manga_alt_title",
        ["manga_id"],
        unique=False,
    )
    op.create_index(
        "ix_manga_alt_title_pgroonga",
        "manga_alt_title",
        ["title"],
        unique=False,
        postgresql_using="pgroonga",
    )
    op.create_table(
        "manga_branch",
        sa.Column("manga_id", sa.Uuid(), nullable=False),
        sa.Column(
            "language",
            sa.Enum("eng", "ukr", name="language"),
            nullable=False,
        ),
        sa.Column("id", sa.Uuid(), nullable=False),
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
        sa.ForeignKeyConstraint(
            ["manga_id"],
            ["manga.id"],
            name=op.f("fk_manga_branch_manga_id_manga"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_manga_branch")),
    )
    op.create_table(
        "manga_chapter",
        sa.Column("branch_id", sa.Uuid(), nullable=False),
        sa.Column("created_by_id", sa.Uuid(), nullable=False),
        sa.Column("title", sa.String(length=250), nullable=False),
        sa.Column("volume", sa.Integer(), nullable=True),
        sa.Column("number", sa.String(length=40), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
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
        sa.ForeignKeyConstraint(
            ["branch_id"],
            ["manga_branch.id"],
            name=op.f("fk_manga_chapter_branch_id_manga_branch"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_manga_chapter")),
    )
    op.create_index(
        op.f("ix_manga_chapter_branch_id"),
        "manga_chapter",
        ["branch_id"],
        unique=False,
    )
    op.create_table(
        "manga_page",
        sa.Column("chapter_id", sa.Uuid(), nullable=False),
        sa.Column("number", sa.Integer(), nullable=False),
        sa.Column("image_path", sa.String(length=250), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(
            ["chapter_id"],
            ["manga_chapter.id"],
            name=op.f("fk_manga_page_chapter_id_manga_chapter"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_manga_page")),
        sa.UniqueConstraint(
            "chapter_id",
            "number",
            name=op.f("uq_manga_page_chapter_id"),
        ),
    )
    op.create_index(
        op.f("ix_manga_page_chapter_id"),
        "manga_page",
        ["chapter_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_manga_page_chapter_id"), table_name="manga_page")
    op.drop_table("manga_page")
    op.drop_index(
        op.f("ix_manga_chapter_branch_id"),
        table_name="manga_chapter",
    )
    op.drop_table("manga_chapter")
    op.drop_table("manga_branch")
    op.drop_index(
        "ix_manga_alt_title_pgroonga",
        table_name="manga_alt_title",
        postgresql_using="pgroonga",
    )
    op.drop_index(
        op.f("ix_manga_alt_title_manga_id"),
        table_name="manga_alt_title",
    )
    op.drop_table("manga_alt_title")
    op.drop_table("manga__manga_tag__secondary")
    op.drop_table("group")
    op.drop_table("user")
    op.drop_table("manga_tag")
    op.drop_table("manga")
