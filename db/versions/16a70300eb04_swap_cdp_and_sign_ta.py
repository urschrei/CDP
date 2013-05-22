"""Swap CDP and Sign table names

Revision ID: 16a70300eb04
Revises: 3bfb6c150903
Create Date: 2013-05-22 14:41:34.214439

"""

# revision identifiers, used by Alembic.
revision = '16a70300eb04'
down_revision = '3bfb6c150903'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.rename_table("sign", "sign_temp")
    op.rename_table("cdp", "sign")
    op.rename_table("sign_temp", "cdp")


def downgrade():
    op.rename_table("cdp", "cdp_temp"),
    op.rename_table("sign", "cdp")
    op.rename_table("cdp_temp", "sign")
