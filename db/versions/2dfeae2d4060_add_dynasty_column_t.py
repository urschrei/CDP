"""Add Dynasty column to Ruler

Revision ID: 2dfeae2d4060
Revises: 4f412f53bdc2
Create Date: 2012-05-30 14:22:21.816370

"""

# revision identifiers, used by Alembic.
revision = '2dfeae2d4060'
down_revision = '4f412f53bdc2'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column(
        "Ruler", sa.Column("dynasty_id", sa.Integer(), sa.ForeignKey("dynasty.id"), nullable=True))


def downgrade():
    op.drop_constraint("ruler_ibfk_2", "Ruler", type="foreignkey")
    op.drop_column("Ruler", "dynasty_id")
