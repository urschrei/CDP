"""adding notes column to Instance

Revision ID: 38d2fd6c3fe0
Revises: 518731a95b23
Create Date: 2012-06-27 22:04:15.251898

"""

# revision identifiers, used by Alembic.
revision = '38d2fd6c3fe0'
down_revision = '518731a95b23'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column(
        "Instance", sa.Column("notes", sa.String(250), nullable=True, unique=False))


def downgrade():
    pass
