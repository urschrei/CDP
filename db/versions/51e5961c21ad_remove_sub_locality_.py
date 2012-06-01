"""remove sub_locality from locality

Revision ID: 51e5961c21ad
Revises: 44453d70d440
Create Date: 2012-06-01 12:15:31.240339

"""

# revision identifiers, used by Alembic.
revision = '51e5961c21ad'
down_revision = '44453d70d440'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.drop_constraint("locality_ibfk_1", "Locality", type="foreignkey")
    op.drop_column("locality", "sub_locality_id")


def downgrade():
    pass
