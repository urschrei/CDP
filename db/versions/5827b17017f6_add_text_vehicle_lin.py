"""Add text vehicle link fields

Revision ID: 5827b17017f6
Revises: 47ebd94a78fc
Create Date: 2012-05-28 14:02:23.992158

"""

# revision identifiers, used by Alembic.
revision = '5827b17017f6'
down_revision = '47ebd94a78fc'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('text_vehicle',
        sa.Column('bm_catalogue', sa.String(100), nullable=True))
    op.add_column('text_vehicle',
        sa.Column('cdli', sa.String(100), nullable=True))


def downgrade():
    op.drop_column('text_vehicle', 'bm_catalogue')
    op.drop_column('cdli', 'bm_catalogue')
