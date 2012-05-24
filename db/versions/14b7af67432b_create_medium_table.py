"""create medium table

Revision ID: 14b7af67432b
Revises: 3ee96eb71903
Create Date: 2012-05-24 10:43:29.661269

"""

# revision identifiers, used by Alembic.
revision = '14b7af67432b'
down_revision = '3ee96eb71903'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'medium',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(50), nullable=False),
    )
    op.create_index('idx_name', 'medium', ['name'])


def downgrade():
    sa.drop_table('medium')