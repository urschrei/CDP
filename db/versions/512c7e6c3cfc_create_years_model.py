"""create Years model

Revision ID: 512c7e6c3cfc
Revises: 140c4962d7a1
Create Date: 2012-05-28 16:58:33.430516

"""

# revision identifiers, used by Alembic.
revision = '512c7e6c3cfc'
down_revision = '140c4962d7a1'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'year',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('year', sa.String(14), nullable=False, unique=True),
        sa.Column('eponym_id', sa.Integer(), sa.ForeignKey("eponym.id"))
    )
    op.create_index('idx_year', 'year', ['year'])


def downgrade():
    op.drop_table('year')