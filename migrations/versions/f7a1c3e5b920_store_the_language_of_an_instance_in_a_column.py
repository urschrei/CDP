"""Store the language of an instance in instance.language_id, and remove the
table instance_language

Revision ID: f7a1c3e5b920
Revises: d4e6b1a9c285
Create Date: 2026-09-13 22:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "f7a1c3e5b920"
down_revision = "d4e6b1a9c285"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    several = bind.execute(
        sa.text(
            "SELECT count(*) FROM (SELECT instance_id FROM instance_language "
            "GROUP BY instance_id HAVING count(*) > 1)"
        )
    ).scalar_one()
    # A column holds one language only. Do not remove the other languages.
    if several:
        raise RuntimeError(f"{several} instances have more than one language")

    with op.batch_alter_table("instance", schema=None) as batch_op:
        batch_op.add_column(sa.Column("language_id", sa.Integer(), nullable=True))
        batch_op.create_index(
            batch_op.f("ix_instance_language_id"), ["language_id"], unique=False
        )
        batch_op.create_foreign_key(
            batch_op.f("fk_instance_language_id_language"),
            "language",
            ["language_id"],
            ["id"],
        )

    op.execute(
        "UPDATE instance SET language_id = (SELECT language_id FROM instance_language "
        "WHERE instance_language.instance_id = instance.id)"
    )

    with op.batch_alter_table("instance_language", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_instance_language_language_id"))
    op.drop_table("instance_language")


def downgrade():
    op.create_table(
        "instance_language",
        sa.Column("instance_id", sa.Integer(), nullable=False),
        sa.Column("language_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["instance_id"],
            ["instance.id"],
            name=op.f("fk_instance_language_instance_id_instance"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["language_id"],
            ["language.id"],
            name=op.f("fk_instance_language_language_id_language"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "instance_id", "language_id", name=op.f("pk_instance_language")
        ),
    )
    with op.batch_alter_table("instance_language", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_instance_language_language_id"),
            ["language_id"],
            unique=False,
        )

    op.execute(
        "INSERT INTO instance_language (instance_id, language_id) "
        "SELECT id, language_id FROM instance WHERE language_id IS NOT NULL"
    )

    with op.batch_alter_table("instance", schema=None) as batch_op:
        batch_op.drop_constraint(
            batch_op.f("fk_instance_language_id_language"), type_="foreignkey"
        )
        batch_op.drop_index(batch_op.f("ix_instance_language_id"))
        batch_op.drop_column("language_id")
