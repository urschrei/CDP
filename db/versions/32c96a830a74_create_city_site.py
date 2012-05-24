"""create city_site

Revision ID: 32c96a830a74
Revises: 33fec814ccdc
Create Date: 2012-05-24 15:30:04.378223

"""

# revision identifiers, used by Alembic.
revision = '32c96a830a74'
down_revision = '33fec814ccdc'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'city_site',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(100), nullable=False),
    )
    op.create_index('idx_name', 'city_site', ['name'])
    op.add_column('city',
        sa.Column('city_site_id', sa.Integer(), sa.ForeignKey('city_site.id'), nullable=True))


def downgrade():
    op.drop_table('city_site')
    op.drop_column('city', 'city_site_id')
