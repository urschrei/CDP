"""create method table

Revision ID: 106748f03f40
Revises: 14b7af67432b
Create Date: 2012-05-24 10:45:57.882092

"""

# revision identifiers, used by Alembic.
revision = '106748f03f40'
down_revision = '14b7af67432b'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'method',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(50), nullable=False),
    )
    op.create_index('idx_name', 'method', ['name'])


def downgrade():
    op.drop_table('method')
