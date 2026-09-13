"""Record edits in the append-only tables change_set and change

Revision ID: a9d2e4f6b813
Revises: f7a1c3e5b920
Create Date: 2026-09-14 09:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "a9d2e4f6b813"
down_revision = "f7a1c3e5b920"
branch_labels = None
depends_on = None

# The models create the same triggers. See cdpp.models.
TRIGGERS = [
    f"CREATE TRIGGER {table}_no_{action.lower()} BEFORE {action} ON {table} "
    f"BEGIN SELECT RAISE(ABORT, '{table} rows cannot be changed or deleted'); END"
    for table in ("change_set", "change")
    for action in ("UPDATE", "DELETE")
]


def upgrade():
    op.create_table(
        "change_set",
        sa.Column("author", sa.String(length=100), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("comment", sa.String(length=500), nullable=True),
        sa.Column("reverts_id", sa.Integer(), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["reverts_id"],
            ["change_set.id"],
            name=op.f("fk_change_set_reverts_id_change_set"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_change_set")),
    )
    with op.batch_alter_table("change_set", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_change_set_reverts_id"), ["reverts_id"], unique=False
        )

    op.create_table(
        "change",
        sa.Column("change_set_id", sa.Integer(), nullable=False),
        sa.Column("kind", sa.String(length=10), nullable=False),
        sa.Column("table_name", sa.String(length=50), nullable=False),
        sa.Column("record_id", sa.Integer(), nullable=False),
        sa.Column("field", sa.String(length=50), nullable=False),
        sa.Column("old_value", sa.JSON(), nullable=False),
        sa.Column("new_value", sa.JSON(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.CheckConstraint("kind IN ('insert', 'update')", name=op.f("ck_change_kind")),
        sa.ForeignKeyConstraint(
            ["change_set_id"],
            ["change_set.id"],
            name=op.f("fk_change_change_set_id_change_set"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_change")),
    )
    with op.batch_alter_table("change", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_change_change_set_id"), ["change_set_id"], unique=False
        )
        batch_op.create_index(
            "ix_change_table_name_record_id",
            ["table_name", "record_id"],
            unique=False,
        )

    for trigger in TRIGGERS:
        op.execute(trigger)


def downgrade():
    # Dropping a table drops its triggers.
    with op.batch_alter_table("change", schema=None) as batch_op:
        batch_op.drop_index("ix_change_table_name_record_id")
        batch_op.drop_index(batch_op.f("ix_change_change_set_id"))
    op.drop_table("change")

    with op.batch_alter_table("change_set", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_change_set_reverts_id"))
    op.drop_table("change_set")
