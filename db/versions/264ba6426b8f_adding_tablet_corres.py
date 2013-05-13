"""adding tablet/corresp association

Revision ID: 264ba6426b8f
Revises: 4b18b9e4c7b7
Create Date: 2012-06-18 21:50:57.268136

"""

# revision identifiers, used by Alembic.
revision = '264ba6426b8f'
down_revision = '4b18b9e4c7b7'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
    "tablet_correspondent",
    sa.Column("tablet_id", sa.Integer(),sa.ForeignKey("tablet.id"), primary_key=True),
    sa.Column("correspondent_id", sa.Integer(), sa.ForeignKey("correspondent.id"), primary_key=True))


def downgrade():
    op.drop_table("tablet_correspondent")
