"""create ruler_tablet many-to-many

Revision ID: 1c237b165a22
Revises: 50a466b2f126
Create Date: 2012-06-01 23:59:32.472021

"""

# revision identifiers, used by Alembic.
revision = '1c237b165a22'
down_revision = '50a466b2f126'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ruler_tablet = op.create_table(
        "ruler_tablet",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("ruler_id", sa.Integer(), sa.ForeignKey("ruler.id"), nullable=False),
        sa.Column("tablet_id", sa.Integer(), sa.ForeignKey("tablet.id"), nullable=False))


def downgrade():
    op.drop_table("ruler_tablet")
