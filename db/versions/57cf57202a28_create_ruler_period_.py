"""create ruler period and subperiod fields

Revision ID: 57cf57202a28
Revises: 1c237b165a22
Create Date: 2012-06-02 23:37:59.225827

"""

# revision identifiers, used by Alembic.
revision = '57cf57202a28'
down_revision = '1c237b165a22'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column(
        "Ruler",
        sa.Column("period_id", sa.Integer(), sa.ForeignKey("period.id"), nullable=False))
    op.add_column(
        "Ruler",
        sa.Column("sub_period_id", sa.Integer(), sa.ForeignKey("sub_period.id"), nullable=True))


def downgrade():
    pass
