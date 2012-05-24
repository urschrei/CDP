"""create function table

Revision ID: 3ee96eb71903
Revises: 420929073034
Create Date: 2012-05-24 10:40:34.273122

"""

# revision identifiers, used by Alembic.
revision = '3ee96eb71903'
down_revision = '420929073034'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'function',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(50), nullable=False),
    )
    op.create_index('idx_name', 'function', ['name'])


def downgrade():
    sa.drop_table('function')
