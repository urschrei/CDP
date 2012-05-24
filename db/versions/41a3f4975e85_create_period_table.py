"""create period table

Revision ID: 41a3f4975e85
Revises: 38380e94b2ad
Create Date: 2012-05-24 11:04:11.430186

"""

# revision identifiers, used by Alembic.
revision = '41a3f4975e85'
down_revision = '38380e94b2ad'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'period',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(150), nullable=False),
        sa.Column('sub_periods', sa.Integer(), sa.ForeignKey('sub_period.id'), nullable=True),
    )
    op.create_index('idx_name', 'period', ['name'])


def downgrade():
    op.drop_table('period')