"""create ruler

Revision ID: 34df0c92b388
Revises: 1a79ae6f5854
Create Date: 2012-05-24 10:08:22.308284

"""

# revision identifiers, used by Alembic.
revision = '34df0c92b388'
down_revision = '1a79ae6f5854'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'ruler',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('rim_ref', sa.String(30), nullable=True),
        sa.Column('city', sa.String(100), sa.ForeignKey('city.name'), nullable=True),
        sa.Column('start_year', sa.String(4), nullable=True),
        sa.Column('end_year', sa.String(4), nullable=True)
    )
    op.create_index('idx_name', 'ruler', ['name'])
    op.create_index('idx_rim', 'ruler', ['rim_ref'])
    op.create_index('idx_start', 'ruler', ['start_year'])
    op.create_index('idx_end', 'ruler', ['end_year'])


def downgrade():
    sa.drop_table('ruler')