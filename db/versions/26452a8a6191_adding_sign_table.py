"""adding sign table

Revision ID: 26452a8a6191
Revises: 2c102926c0e0
Create Date: 2012-06-21 17:08:50.677187

"""

# revision identifiers, used by Alembic.
revision = '26452a8a6191'
down_revision = '2c102926c0e0'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        "sign",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(50), nullable=False, index=True),
        sa.Column("number", sa.String(10), nullable=True, index=True))


def downgrade():
    op.drop_table("sign")
