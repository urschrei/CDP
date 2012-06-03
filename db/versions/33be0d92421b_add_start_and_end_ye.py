"""add start and end years to ruler-dynasty association

Revision ID: 33be0d92421b
Revises: 2d6ef64d441d
Create Date: 2012-06-03 01:01:36.436876

"""

# revision identifiers, used by Alembic.
revision = '33be0d92421b'
down_revision = '2d6ef64d441d'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column(
        "ruler_Dynasty", sa.Column("start_year_id", sa.Integer(), sa.ForeignKey("year.id"), nullable=True))
    op.add_column(
        "ruler_Dynasty", sa.Column("end_year_id", sa.Integer(), sa.ForeignKey("year.id"), nullable=True))


def downgrade():
    pass
