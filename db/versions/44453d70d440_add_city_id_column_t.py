"""add city_id column to city_site

Revision ID: 44453d70d440
Revises: 33ed8de7da48
Create Date: 2012-06-01 12:02:01.960592

"""

# revision identifiers, used by Alembic.
revision = '44453d70d440'
down_revision = '33ed8de7da48'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column(
        "City_Site", sa.Column("city_id", sa.Integer(), sa.ForeignKey("city.id"), nullable=False))


def downgrade():
    pass
