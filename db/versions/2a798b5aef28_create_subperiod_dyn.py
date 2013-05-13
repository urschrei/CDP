"""create subperiod_dynasty association object

Revision ID: 2a798b5aef28
Revises: 39c0b5394346
Create Date: 2012-06-08 22:25:27.533356

"""

# revision identifiers, used by Alembic.
revision = '2a798b5aef28'
down_revision = '39c0b5394346'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        "subperiod_dynasty",
        sa.Column("subperiod_id", sa.Integer(), sa.ForeignKey("sub_period.id", onupdate="CASCADE", ondelete="CASCADE"), primary_key=True),
        sa.Column("dynasty_id", sa.Integer(), sa.ForeignKey("dynasty.id", onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)
    )


def downgrade():
    pass
