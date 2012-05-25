"""create tablet table

Revision ID: 79a36c9d1f0
Revises: 2f02b5f5e769
Create Date: 2012-05-25 14:24:40.224291

"""

# revision identifiers, used by Alembic.
revision = '79a36c9d1f0'
down_revision = '2f02b5f5e769'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'tablet',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('museum_number', sa.String(75), nullable=False, unique=True),
        sa.Column('medium_id', sa.Integer(), sa.ForeignKey('medium.id'), nullable=False),
        sa.Column('script_type_id', sa.Integer(), sa.ForeignKey('script_type.id'), nullable=True),
        # sa.Column('locality_id', sa.Integer(), sa.ForeignKey('locality.id'), nullable=False),
        # sa.Column('sub_locality_id', sa.Integer(), sa.ForeignKey('sub_locality.id'), nullable=False),
        sa.Column('city_id', sa.Integer(), sa.ForeignKey('city.id'), nullable=True),
        sa.Column('origin_city_id', sa.Integer(), sa.ForeignKey('city.id'), nullable=True),
        # sa.Column('city_site_id', sa.Integer(), sa.ForeignKey('city_site.id'), nullable=False),
        sa.Column('publication', sa.String(200), nullable=True),
        sa.Column('period_id', sa.Integer(), sa.ForeignKey('period.id'), nullable=False),
        sa.Column('from_id', sa.Integer(), sa.ForeignKey('ruler.id'), nullable=True),
        sa.Column('to_id', sa.Integer(), sa.ForeignKey('ruler.id'), nullable=True),
        sa.Column('year', sa.String(10), nullable=True),
        sa.Column('month', sa.String(10), nullable=True),
        sa.Column('day', sa.String(10), nullable=True),
        sa.Column('eponym_id', sa.Integer(), sa.ForeignKey('eponym.id'), nullable=True),
        sa.Column('text_vehicle_id', sa.Integer(), sa.ForeignKey('text_vehicle.id'), nullable=True),
        sa.Column('notes', sa.String(500), nullable=True),
    )
    op.create_index('idx_museum_number', 'tablet', ['museum_number'])


def downgrade():
    op.drop_table('tablet')
