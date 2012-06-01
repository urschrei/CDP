"""remove unneeded ruler fields

Revision ID: 4cc2737c71fe
Revises: 53600f14b53b
Create Date: 2012-06-01 14:50:07.092548

"""

# revision identifiers, used by Alembic.
revision = '4cc2737c71fe'
down_revision = '53600f14b53b'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.drop_constraint("ruler_ibfk_1", "Ruler", type="foreignkey")
    op.drop_column("Ruler", "city_id")
    op.drop_column("Ruler", "rim_ref")


def downgrade():
    pass
