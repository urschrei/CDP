"""add reign to tablet

Revision ID: 1829a641de7f
Revises: 5698ffeb9a5b
Create Date: 2012-06-09 13:45:42.174499

"""

# revision identifiers, used by Alembic.
revision = '1829a641de7f'
down_revision = '5698ffeb9a5b'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column("Tablet", sa.Column("reign_id", sa.Integer(), sa.ForeignKey("reign.id"), nullable=True))


def downgrade():
    pass
