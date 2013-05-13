"""adding filename column to Instance

Revision ID: 37d8aa5e5237
Revises: 38d2fd6c3fe0
Create Date: 2012-06-29 21:52:20.915513

"""

# revision identifiers, used by Alembic.
revision = '37d8aa5e5237'
down_revision = '38d2fd6c3fe0'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column(
        "Instance", sa.Column("filename", sa.String(50), nullable=False, unique=True))


def downgrade():
    pass
