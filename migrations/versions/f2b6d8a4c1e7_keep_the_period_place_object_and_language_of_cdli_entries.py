"""Keep the period, place, object and language of CDLI entries

Revision ID: f2b6d8a4c1e7
Revises: e5a1c7d3f920
Create Date: 2026-09-13 15:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "f2b6d8a4c1e7"
down_revision = "e5a1c7d3f920"
branch_labels = None
depends_on = None

COLUMNS = ("period", "provenience", "object_type", "material", "language")


def upgrade():
    # The columns are empty until the next "cdpp import-cdli".
    with op.batch_alter_table("cdli_artifact", schema=None) as batch_op:
        for name in COLUMNS:
            batch_op.add_column(sa.Column(name, sa.String(length=200), nullable=True))


def downgrade():
    with op.batch_alter_table("cdli_artifact", schema=None) as batch_op:
        for name in reversed(COLUMNS):
            batch_op.drop_column(name)
