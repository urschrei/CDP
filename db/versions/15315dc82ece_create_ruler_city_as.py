"""create ruler_city association table

Revision ID: 15315dc82ece
Revises: 33be0d92421b
Create Date: 2012-06-03 23:17:13.839799

"""

# revision identifiers, used by Alembic.
revision = '15315dc82ece'
down_revision = '33be0d92421b'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ruler_city = op.create_table(
        "ruler_city",
        sa.Column("ruler_id", sa.Integer(), sa.ForeignKey("ruler.id"), primary_key=True),
        sa.Column("city_id", sa.Integer(), sa.ForeignKey("city.id"), primary_key=True))


def downgrade():
    op.drop_table("ruler_city")
