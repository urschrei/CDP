"""Fix Sign <--> CDP relationship

Revision ID: 1e1a5bcdef73
Revises: 16a70300eb04
Create Date: 2013-05-22 14:47:02.635549

"""

# revision identifiers, used by Alembic.
revision = '1e1a5bcdef73'
down_revision = '16a70300eb04'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.drop_constraint("fk_cdp_sign", "cdp", type="foreignkey")
    op.alter_column(
        table_name="cdp",
        column_name="cdp_id",
        new_column_name="sign_id",
        existing_type=sa.Integer,
        existing_nullable=False)
    op.create_foreign_key(
        "fk_sign_cdp",
        "cdp",
        "sign",
        ["sign_id"],
        ["id"])


def downgrade():
    op.drop_constraint("fk_sign_cdp", "cdp", type="foreignkey")
    op.alter_column(
        table_name="cdp",
        column_name="sign_id",
        new_column_name="cdp_id",
        existing_type=sa.Integer,
        existing_nullable=False)
    op.create_foreign_key(
        "fk_cdp_sign",
        "sign",
        "cdp",
        ["cdp_id"],
        ["id"])
