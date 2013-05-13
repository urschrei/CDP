"""add reign table

Revision ID: e97dc8d2db3
Revises: 2a798b5aef28
Create Date: 2012-06-09 00:06:53.507047

"""

# revision identifiers, used by Alembic.
revision = 'e97dc8d2db3'
down_revision = '2a798b5aef28'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        "reign",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("rim_ref", sa.String(50), nullable=False, index=True),
        sa.Column("city_id", sa.Integer(), sa.ForeignKey("city.id"), nullable=True),
        sa.Column("start_date", sa.Integer(), sa.ForeignKey("year.id"), nullable=True),
        sa.Column("end_date", sa.Integer(), sa.ForeignKey("year.id"), nullable=True),
        sa.Column("dynasty_id", sa.Integer(), sa.ForeignKey("dynasty.id"), nullable=True),
        sa.Column("period_id", sa.Integer(), sa.ForeignKey("period.id"), nullable=False),
        sa.Column("sub_period_id", sa.Integer, sa.ForeignKey("sub_period.id"), nullable=True))


def downgrade():
    op.drop_table("reign")
