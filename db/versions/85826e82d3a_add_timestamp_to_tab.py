"""add timestamp to tablet

Revision ID: 85826e82d3a
Revises: 1829a641de7f
Create Date: 2012-06-12 11:18:54.721580

"""

# revision identifiers, used by Alembic.
revision = '85826e82d3a'
down_revision = '1829a641de7f'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column(
        "Tablet", sa.Column("timestamp", sa.DateTime(timezone=True), default=sa.func.now(), nullable=False))


def downgrade():
    pass
