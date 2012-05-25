"""create eponym table

Revision ID: 2f02b5f5e769
Revises: 1474a7665ab0
Create Date: 2012-05-25 10:59:04.720025

"""

# revision identifiers, used by Alembic.
revision = '2f02b5f5e769'
down_revision = '1474a7665ab0'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'eponym',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(50), nullable=False),
        sa.Column('year', sa.String(10), nullable=True)
    )
    op.create_index('idx_name', 'eponym', ['name'])


def downgrade():
    op.drop_table('eponym')