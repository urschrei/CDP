"""Add Dynasty column to Ruler

Revision ID: 2dfeae2d4060
Revises: 4f412f53bdc2
Create Date: 2012-05-30 14:22:21.816370

"""

# revision identifiers, used by Alembic.
revision = '2dfeae2d4060'
down_revision = '3041cb6ecafa'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column(
        "Instance", sa.Column("tablet_id", sa.Integer(), sa.ForeignKey("tablet.id"), nullable=False))


def downgrade():
    op.drop_constraint("tablet_ibfk_14", "Tablet", type="foreignkey")
    op.drop_column("Tablet", "dynasty_id")
    op.drop_table("dynasty")
