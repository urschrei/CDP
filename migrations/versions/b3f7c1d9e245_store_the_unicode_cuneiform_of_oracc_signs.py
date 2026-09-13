"""Store the Unicode cuneiform of each sign and form in the Oracc Sign List snapshot

Revision ID: b3f7c1d9e245
Revises: a9d2e4f6b813
Create Date: 2026-09-14 12:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "b3f7c1d9e245"
down_revision = "a9d2e4f6b813"
branch_labels = None
depends_on = None


def upgrade():
    # The column is empty until the next "cdpp import-oracc-signs".
    with op.batch_alter_table("oracc_sign", schema=None) as batch_op:
        batch_op.add_column(sa.Column("cuneiform", sa.String(length=30), nullable=True))


def downgrade():
    with op.batch_alter_table("oracc_sign", schema=None) as batch_op:
        batch_op.drop_column("cuneiform")
