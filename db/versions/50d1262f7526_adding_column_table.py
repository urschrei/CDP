"""adding column table

Revision ID: 50d1262f7526
Revises: 49bce4ecd7ca
Create Date: 2012-06-21 15:36:05.501713

"""

# revision identifiers, used by Alembic.
revision = '50d1262f7526'
down_revision = '49bce4ecd7ca'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        "column",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("number", sa.String(5), nullable=False, index=True))


def downgrade():
    op.drop_table("column")
