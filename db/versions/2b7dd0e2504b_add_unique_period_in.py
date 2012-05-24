"""add unique period index

Revision ID: 2b7dd0e2504b
Revises: 2694403b011d
Create Date: 2012-05-28 15:18:38.519910

"""

# revision identifiers, used by Alembic.
revision = '2b7dd0e2504b'
down_revision = '2694403b011d'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_unique_constraint("uq_name", "period", ["name"])


def downgrade():
    op.drop_constraint("period", "uq_name", type="unique")
