"""add period dates

Revision ID: 2694403b011d
Revises: 5827b17017f6
Create Date: 2012-05-28 14:50:45.176099

"""

# revision identifiers, used by Alembic.
revision = '2694403b011d'
down_revision = '5827b17017f6'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('period',
        sa.Column('from_date', sa.String(50), nullable=True))
    op.add_column('period',
        sa.Column('to_date', sa.String(50), nullable=True))


def downgrade():
    op.drop_column('period', 'from_date')
    op.drop_column('period', 'to_date')