"""create genre table

Revision ID: 15ce433d0448
Revises: 106748f03f40
Create Date: 2012-05-24 10:51:55.168150

"""

# revision identifiers, used by Alembic.
revision = '15ce433d0448'
down_revision = '106748f03f40'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'genre',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(100), nullable=False),
    )
    op.create_index('idx_name', 'genre', ['name'])


def downgrade():
    op.drop_table('genre')