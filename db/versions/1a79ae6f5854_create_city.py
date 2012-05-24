"""create city

Revision ID: 1a79ae6f5854
Revises: 1dd770a954f0
Create Date: 2012-05-24 10:00:01.743534

"""

# revision identifiers, used by Alembic.
revision = '1a79ae6f5854'
down_revision = '1dd770a954f0'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'city',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('locality_id', sa.Integer(), sa.ForeignKey('locality.id'), nullable=False)
    )
    op.create_index('idx_name', 'city', ['name'])


def downgrade():
    op.drop_table('city')