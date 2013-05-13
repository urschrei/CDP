"""adding tablet ID to instance

Revision ID: 518731a95b23
Revises: 4eb053a8df5f
Create Date: 2012-06-22 17:54:54.362335

"""

# revision identifiers, used by Alembic.
revision = '518731a95b23'
down_revision = '4eb053a8df5f'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column(
        "Instance", sa.Column("tablet_id", sa.Integer(), sa.ForeignKey("tablet.id"), nullable=False))

def downgrade():
    pass
