"""city site and period changes

Revision ID: 33ed8de7da48
Revises: 2cc7f0bad778
Create Date: 2012-06-01 11:55:23.710976

"""

# revision identifiers, used by Alembic.
revision = '33ed8de7da48'
down_revision = '2cc7f0bad778'

from alembic import op
import sqlalchemy as sa


def upgrade():
    pass
    # remove city_site from city
    op.drop_constraint("city_ibfk_2", "City", type="foreignkey")
    op.drop_column("City", "city_site_id")
    # remove sub_period from period
    op.drop_constraint("period_ibfk_1", "Period", type="foreignkey")
    op.drop_column("Period", "sub_period_id")

def downgrade():
    pass
