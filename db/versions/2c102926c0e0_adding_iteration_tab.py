"""adding iteration table

Revision ID: 2c102926c0e0
Revises: 1b7bbc51cb1c
Create Date: 2012-06-21 15:44:40.062494

"""

# revision identifiers, used by Alembic.
revision = '2c102926c0e0'
down_revision = '1b7bbc51cb1c'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        "iteration",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("number", sa.String(5), nullable=False, index=True))


def downgrade():
    op.drop_table("iteration")