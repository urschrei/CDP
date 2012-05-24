"""create locality

Revision ID: 1dd770a954f0
Revises: 257b49196f96
Create Date: 2012-05-24 09:51:22.161598

"""

# revision identifiers, used by Alembic.
revision = '1dd770a954f0'
down_revision = '257b49196f96'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'locality',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('area', sa.String(100), nullable=False)
    )
    op.create_index('idx_area', 'locality', ['area'])


def downgrade():
    sa.drop_table('locality')
