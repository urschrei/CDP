"""create script type

Revision ID: 14a24e87292
Revises: 34df0c92b388
Create Date: 2012-05-24 10:29:09.267749

"""

# revision identifiers, used by Alembic.
revision = '14a24e87292'
down_revision = '34df0c92b388'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'script_type',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('script', sa.String(50), nullable=False),
    )
    op.create_index('idx_script', 'script_type', ['script'])


def downgrade():
    sa.drop_table('script_type')