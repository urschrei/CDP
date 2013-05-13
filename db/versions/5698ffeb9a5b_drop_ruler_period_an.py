"""drop ruler period and sub_period

Revision ID: 5698ffeb9a5b
Revises: 10feaf71667e
Create Date: 2012-06-09 01:41:07.673701

"""

# revision identifiers, used by Alembic.
revision = '5698ffeb9a5b'
down_revision = '10feaf71667e'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.drop_constraint("ruler_ibfk_1", "ruler", type="foreignkey")
    op.drop_constraint("ruler_ibfk_2", "ruler", type="foreignkey")
    op.drop_column("Ruler", "period_id")
    op.drop_column("Ruler", "sub_period_id")


def downgrade():
    pass
