"""create ruler_tablet association object

Revision ID: 39c0b5394346
Revises: 15315dc82ece
Create Date: 2012-06-08 21:47:38.011511

"""

# revision identifiers, used by Alembic.
revision = '39c0b5394346'
down_revision = '15315dc82ece'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        "ruler_tablet",
        sa.Column("ruler_id", sa.Integer(), sa.ForeignKey("ruler.id", onupdate="CASCADE", ondelete="CASCADE"), primary_key=True),
        sa.Column("tablet_id", sa.Integer(), sa.ForeignKey("tablet.id", onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)
    )


def downgrade():
    pass
