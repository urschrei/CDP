"""create sub-period table

Revision ID: 38380e94b2ad
Revises: 15ce433d0448
Create Date: 2012-05-24 10:56:56.886072

"""

# revision identifiers, used by Alembic.
revision = '38380e94b2ad'
down_revision = '15ce433d0448'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'sub_period',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(100), nullable=False),
    )
    op.create_index('idx_name', 'sub_period', ['name'])


def downgrade():
    sa.drop_table('sub_period')