"""adding line table

Revision ID: 1b7bbc51cb1c
Revises: 50d1262f7526
Create Date: 2012-06-21 15:43:39.140577

"""

# revision identifiers, used by Alembic.
revision = '1b7bbc51cb1c'
down_revision = '50d1262f7526'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        "line",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("number", sa.String(5), nullable=False, index=True))


def downgrade():
    op.drop_table("line")