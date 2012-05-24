"""create language

Revision ID: 420929073034
Revises: 14a24e87292
Create Date: 2012-05-24 10:36:42.330839

"""

# revision identifiers, used by Alembic.
revision = '420929073034'
down_revision = '14a24e87292'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'language',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(100), nullable=False),
    )
    op.create_index('idx_name', 'language', ['name'])


def downgrade():
    sa.drop_table('language')
