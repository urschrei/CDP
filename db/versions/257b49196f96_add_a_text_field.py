"""Add a text field

Revision ID: 257b49196f96
Revises: 31a0ee06ad2e
Create Date: 2012-05-16 13:44:02.007767

"""

# revision identifiers, used by Alembic.
revision = '257b49196f96'
down_revision = '31a0ee06ad2e'

from alembic import op
import sqlalchemy as sa


def upgrade():
    pass
    op.add_column('test', sa.Column('text_field', sa.Text))


def downgrade():
    op.drop_column('test', 'text_field')

