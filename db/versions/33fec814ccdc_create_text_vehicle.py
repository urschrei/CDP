"""create text vehicle

Revision ID: 33fec814ccdc
Revises: 41a3f4975e85
Create Date: 2012-05-24 14:40:26.335757

"""

# revision identifiers, used by Alembic.
revision = '33fec814ccdc'
down_revision = '41a3f4975e85'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'text_vehicle',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(100), nullable=False),
    )
    op.create_index('idx_name', 'text_vehicle', ['name'])


def downgrade():
    op.drop_table('text_vehicle')
