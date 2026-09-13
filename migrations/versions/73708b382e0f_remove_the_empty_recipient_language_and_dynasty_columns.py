"""Remove the empty recipient, language and dynasty columns of tablets

Revision ID: 73708b382e0f
Revises: f2b6d8a4c1e7
Create Date: 2026-09-13 14:29:43.563379

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "73708b382e0f"
down_revision = "f2b6d8a4c1e7"
branch_labels = None
depends_on = None

# tablet_correspondent keeps the recipients, and instance.language_id keeps the
# languages. No tablet has a dynasty.
COLUMNS = (
    ("to_id", "correspondent"),
    ("language_id", "language"),
    ("dynasty_id", "dynasty"),
)


def upgrade():
    filled = " OR ".join(f"{column} IS NOT NULL" for column, _ in COLUMNS)
    count = op.get_bind().scalar(sa.text(f"SELECT count(*) FROM tablet WHERE {filled}"))
    if count:
        raise RuntimeError(
            f"{count} tablets have a value in to_id, language_id or dynasty_id. "
            "Move the values before this migration removes the columns."
        )
    with op.batch_alter_table("tablet", schema=None) as batch_op:
        for column, target in COLUMNS:
            batch_op.drop_index(batch_op.f(f"ix_tablet_{column}"))
            batch_op.drop_constraint(
                batch_op.f(f"fk_tablet_{column}_{target}"), type_="foreignkey"
            )
            batch_op.drop_column(column)


def downgrade():
    with op.batch_alter_table("tablet", schema=None) as batch_op:
        for column, target in COLUMNS:
            batch_op.add_column(sa.Column(column, sa.Integer(), nullable=True))
            batch_op.create_foreign_key(
                batch_op.f(f"fk_tablet_{column}_{target}"), target, [column], ["id"]
            )
            batch_op.create_index(
                batch_op.f(f"ix_tablet_{column}"), [column], unique=False
            )
