"""add period_id to sub_period

Revision ID: 53600f14b53b
Revises: 51e5961c21ad
Create Date: 2012-06-01 12:26:04.578176

"""

# revision identifiers, used by Alembic.
revision = '53600f14b53b'
down_revision = '51e5961c21ad'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column(
        "Sub_Period",
        sa.Column("period_id", sa.Integer(), sa.ForeignKey("period.id"), nullable=False))


def downgrade():
    pass
