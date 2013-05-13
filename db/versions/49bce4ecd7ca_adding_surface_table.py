"""adding surface table

Revision ID: 49bce4ecd7ca
Revises: 25dbdbfd8d0f
Create Date: 2012-06-21 15:05:06.480605

"""

# revision identifiers, used by Alembic.
revision = '49bce4ecd7ca'
down_revision = '25dbdbfd8d0f'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        "surface",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(20), nullable=False, index=True))


def downgrade():
    op.drop_table("surface")