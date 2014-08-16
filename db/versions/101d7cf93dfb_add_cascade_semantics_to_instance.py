"""Add Cascade semantics to Instance

Revision ID: 101d7cf93dfb
Revises: 54903f3b1315
Create Date: 2014-08-15 22:25:13.613093

"""

# revision identifiers, used by Alembic.
revision = '101d7cf93dfb'
down_revision = '54903f3b1315'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.drop_constraint("instance_ibfk_1", "instance", type_="foreignkey")
    op.drop_constraint("instance_ibfk_7", "instance", type_="foreignkey")
    op.create_foreign_key(
        None,
        "instance",
        "sign",
        ["sign_id"],
        ["id"],
        onupdate="CASCADE", ondelete="CASCADE")
    op.create_foreign_key(
        None,
        "instance",
        "tablet",
        ["tablet_id"],
        ["id"],
        onupdate="CASCADE", ondelete="CASCADE")


def downgrade():
    op.drop_constraint("fk_instance_sign_id_sign", "instance", type_="foreignkey")
    op.drop_constraint("fk_instance_tablet_id_tablet", "instance", type_="foreignkey")
    op.create_foreign_key(
        "instance_ibfk_1",
        "instance",
        "sign",
        ["sign_id"],
        ["id"])
    op.create_foreign_key(
        "instance_ibfk_7",
        "instance",
        "tablet",
        ["tablet_id"],
        ["id"])
