"""add eponym to tablet

Revision ID: 4b18b9e4c7b7
Revises: 85826e82d3a
Create Date: 2012-06-18 17:13:57.243026

"""

# revision identifiers, used by Alembic.
revision = '4b18b9e4c7b7'
down_revision = '85826e82d3a'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column(
        "Tablet", sa.Column("eponym_id", sa.Integer(), sa.ForeignKey("eponym.id"), nullable=True))


def downgrade():
    pass
