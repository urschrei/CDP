"""create correspondents table

Revision ID: 439e06a010f1
Revises: 4d972ee7f65
Create Date: 2012-05-28 09:47:34.756533

"""

# revision identifiers, used by Alembic.
revision = '439e06a010f1'
down_revision = '4d972ee7f65'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'correspondent',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('ruler_id', sa.Integer(), sa.ForeignKey('ruler.id'), nullable=True),
        sa.Column('non_ruler_id', sa.Integer(), sa.ForeignKey('non_ruler_corresp.id'), nullable=True)
    )


def downgrade():
    op.drop_table('correspondent')
