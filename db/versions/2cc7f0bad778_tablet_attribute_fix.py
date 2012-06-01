"""tablet attribute fixes

Revision ID: 2cc7f0bad778
Revises: 2dfeae2d4060
Create Date: 2012-06-01 11:14:32.489988

"""

# revision identifiers, used by Alembic.
revision = '2cc7f0bad778'
down_revision = '2dfeae2d4060'

from alembic import op
import sqlalchemy as sa


def upgrade():
    pass
    # add locality to Tablet
    op.add_column(
        "Tablet", sa.Column("locality_id", sa.Integer(), sa.ForeignKey("locality.id"), nullable=True))
    # add sub-locality to Tablet
    op.add_column(
        "Tablet", sa.Column("sub_locality_id", sa.Integer(), sa.ForeignKey("sub_locality.id"), nullable=True))
    # add sub-period to Tablet
    op.add_column(
        "Tablet", sa.Column("sub_period_id", sa.Integer(), sa.ForeignKey("sub_period.id"), nullable=True))
    # add city site to Tablet
    op.add_column(
        "Tablet", sa.Column("city_site_id", sa.Integer(), sa.ForeignKey("city_site.id"), nullable=True))


def downgrade():
    pass
    # remove foreign key constraints
    op.drop_constraint("tablet_ibfk_15", "Tablet", type="foreignkey")
    op.drop_constraint("tablet_ibfk_16", "Tablet", type="foreignkey")
    op.drop_constraint("tablet_ibfk_17", "Tablet", type="foreignkey")
    op.drop_constraint("tablet_ibfk_18", "Tablet", type="foreignkey")
    op.drop_column("Tablet", "locality_id")
    op.drop_column("Tablet", "sub_locality_id")
    op.drop_column("Tablet", "sub_period_id")
    op.drop_column("Tablet", "city_site_id")
