"""add ruler column to Reign

Revision ID: 10feaf71667e
Revises: e97dc8d2db3
Create Date: 2012-06-09 01:28:44.786496

"""

# revision identifiers, used by Alembic.
revision = '10feaf71667e'
down_revision = 'e97dc8d2db3'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column("Reign", sa.Column("ruler_id", sa.Integer(), sa.ForeignKey("ruler.id"), nullable=False))


def downgrade():
    pass
