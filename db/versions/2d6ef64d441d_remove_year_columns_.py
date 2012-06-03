"""remove year columns from Ruler

Revision ID: 2d6ef64d441d
Revises: 57cf57202a28
Create Date: 2012-06-03 00:49:32.505812

"""

# revision identifiers, used by Alembic.
revision = '2d6ef64d441d'
down_revision = '57cf57202a28'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.drop_column("Ruler", "start_year")
    op.drop_column("Ruler", "end_year")


def downgrade():
    pass
