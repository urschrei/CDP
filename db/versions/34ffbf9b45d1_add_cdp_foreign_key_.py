"""Add CDP foreign key constraint to Sign

Revision ID: 34ffbf9b45d1
Revises: 195d22b61896
Create Date: 2013-05-21 12:45:59.511871

"""

# revision identifiers, used by Alembic.
revision = '34ffbf9b45d1'
down_revision = '195d22b61896'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_foreign_key(
        "fk_cdp_sign",
        "sign",
        "cdp",
        ["cdp_id"],
        ["id"])


def downgrade():
    op.drop_constraint("fk_cdp_sign", "sign")
