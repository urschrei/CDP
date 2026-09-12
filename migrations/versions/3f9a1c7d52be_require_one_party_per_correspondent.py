"""Require exactly one party per correspondent

Revision ID: 3f9a1c7d52be
Revises: c17301121c9c
Create Date: 2026-09-13 10:00:00.000000

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "3f9a1c7d52be"
down_revision = "c17301121c9c"
branch_labels = None
depends_on = None


def upgrade():
    # Autogenerate does not detect check constraints.
    with op.batch_alter_table("correspondent", schema=None) as batch_op:
        batch_op.create_check_constraint(
            batch_op.f("ck_correspondent_one_party"),
            "(ruler_id IS NULL) != (non_ruler_id IS NULL)",
        )


def downgrade():
    with op.batch_alter_table("correspondent", schema=None) as batch_op:
        batch_op.drop_constraint(
            batch_op.f("ck_correspondent_one_party"), type_="check"
        )
