"""Test migration

Revision ID: 31a0ee06ad2e
Revises: None
Create Date: 2012-05-13 14:38:14.070612

"""

# revision identifiers, used by Alembic.
revision = '31a0ee06ad2e'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'test',
        sa.Column('id', sa.Integer, primary_key=True),
    )


def downgrade():
    op.drop_table('test')
