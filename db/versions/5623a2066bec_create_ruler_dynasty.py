"""create ruler_dynasty association table

Revision ID: 5623a2066bec
Revises: 4cc2737c71fe
Create Date: 2012-06-01 15:15:40.995859

"""

# revision identifiers, used by Alembic.
revision = '5623a2066bec'
down_revision = '4cc2737c71fe'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
    "ruler_dynasty",
    sa.Column("id", sa.Integer(), primary_key=True),
    sa.Column("ruler_id", sa.Integer(),sa.ForeignKey("ruler.id"), nullable=False),
    sa.Column("dynasty_id", sa.Integer(), sa.ForeignKey("dynasty.id"), nullable=False),
    sa.Column("rim_ref", sa.String(75)))


def downgrade():
    op.drop_table("ruler_dynasty")
