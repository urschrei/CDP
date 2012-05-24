"""Add all of the unique indices

Revision ID: 47ebd94a78fc
Revises: 439e06a010f1
Create Date: 2012-05-28 12:10:05.182716

"""

# revision identifiers, used by Alembic.
revision = '47ebd94a78fc'
down_revision = '439e06a010f1'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_unique_constraint("uq_name", "non_ruler_corresp", ["name"])
    op.create_unique_constraint("uq_area", "locality", ["area"])
    op.create_unique_constraint("uq_name", "sub_locality", ["name"])
    op.create_unique_constraint("uq_name", "method", ["name"])
    op.create_unique_constraint("uq_script", "script_type", ["script"])
    op.create_unique_constraint("uq_name", "medium", ["name"])
    op.create_unique_constraint("uq_name", "genre", ["name"])
    op.create_unique_constraint("uq_name", "function", ["name"])
    op.create_unique_constraint("uq_name", "text_vehicle", ["name"])
    op.create_unique_constraint("uq_name", "eponym", ["name"])
    op.create_unique_constraint("uq_name", "city", ["name"])
    op.create_unique_constraint("uq_name", "city_site", ["name"])
    op.create_unique_constraint("uq_name", "ruler", ["name"])


def downgrade():
    op.drop_constraint("non_ruler_corresp", "uq_name", type="unique")
    op.drop_constraint("locality", "uq_area", type="unique")
    op.drop_constraint("sub_locality", "uq_name", type="unique")
    op.drop_constraint("method", "uq_name", type="unique")
    op.drop_constraint("script_type", "uq_name", type="unique")
    op.drop_constraint("medium", "uq_name", type="unique")
    op.drop_constraint("genre", "uq_name", type="unique")
    op.drop_constraint("function", "uq_name", type="unique")
    op.drop_constraint("text_vehicle", "uq_name", type="unique")
    op.drop_constraint("eponym", "uq_name", type="unique")
    op.drop_constraint("city", "uq_name", type="unique")
    op.drop_constraint("city_site", "uq_name", type="unique")
    op.drop_constraint("ruler", "uq_name", type="unique")
    

