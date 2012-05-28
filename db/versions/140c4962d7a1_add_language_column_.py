"""add language column to Tablet

Revision ID: 140c4962d7a1
Revises: f1d79dfe164
Create Date: 2012-05-28 15:42:25.210468

"""

# revision identifiers, used by Alembic.
revision = '140c4962d7a1'
down_revision = 'f1d79dfe164'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('tablet',
        sa.Column('language_id', sa.Integer(), nullable=True))


def downgrade():
    op.drop_column('tablet', 'language_id')
