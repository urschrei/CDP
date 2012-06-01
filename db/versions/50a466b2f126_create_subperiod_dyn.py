"""create subperiod_dynasty many-to-many

Revision ID: 50a466b2f126
Revises: 5623a2066bec
Create Date: 2012-06-01 19:50:32.515697

"""

# revision identifiers, used by Alembic.
revision = '50a466b2f126'
down_revision = '5623a2066bec'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
    "subperiod_dynasty",
    sa.Column("id", sa.Integer(), primary_key=True),
    sa.Column("dynasty_id", sa.Integer(),sa.ForeignKey("dynasty.id"), nullable=False),
    sa.Column("subperiod_id", sa.Integer(), sa.ForeignKey("sub_period.id"), nullable=False))


def downgrade():
    op.drop_table("subperiod_dynasty")
