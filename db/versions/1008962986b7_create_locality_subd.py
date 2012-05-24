"""create locality_subdivision

Revision ID: 1008962986b7
Revises: 32c96a830a74
Create Date: 2012-05-24 16:00:20.656966

"""

# revision identifiers, used by Alembic.
revision = '1008962986b7'
down_revision = '32c96a830a74'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'sub_locality',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(100), nullable=False),
    )
    op.create_index('idx_name', 'sub_locality', ['name'])
    op.add_column('locality',
        sa.Column('sub_locality_id', sa.Integer(), sa.ForeignKey('sub_locality.id'), nullable=True))


def downgrade():
    op.drop_table('sub_locality')
    op.drop_column('city', 'sub_locality_id')
