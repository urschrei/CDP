"""create non-ruler correspondents table

Revision ID: 4d972ee7f65
Revises: 79a36c9d1f0
Create Date: 2012-05-28 09:44:40.083961

"""

# revision identifiers, used by Alembic.
revision = '4d972ee7f65'
down_revision = '79a36c9d1f0'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'non_ruler_corresp',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(100), nullable=False),
    )
    op.create_index('idx_name', 'non_ruler_corresp', ['name'])


def downgrade():
    op.drop_table('non_ruler_corresp')
