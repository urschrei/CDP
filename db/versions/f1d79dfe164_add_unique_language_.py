"""add unique language index

Revision ID: f1d79dfe164
Revises: 2b7dd0e2504b
Create Date: 2012-05-28 15:33:39.974153

"""

# revision identifiers, used by Alembic.
revision = 'f1d79dfe164'
down_revision = '2b7dd0e2504b'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_unique_constraint("uq_name", "language", ["name"])


def downgrade():
    op.drop_constraint("period", "language", type="unique")

