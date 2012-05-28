"""modify tablet year and eponym

Revision ID: 1f48027357c
Revises: 512c7e6c3cfc
Create Date: 2012-05-28 17:08:29.012747

"""

# revision identifiers, used by Alembic.
revision = '1f48027357c'
down_revision = '512c7e6c3cfc'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.drop_constraint("tablet_ibfk_8", "tablet", type="foreignkey")
    op.drop_column("tablet", "eponym_id")
    op.drop_column("eponym", "year")
    op.drop_column("tablet", "year")
    # create year foreign key on tablet
    op.add_column("tablet",
        sa.Column("year_id", sa.Integer(), sa.ForeignKey("year.id"), nullable=True))


def downgrade():
    op.add_column("eponym", "year", sa.String(10))
    op.add_column("tablet", "year", sa.string(10))
    op.add_column("tablet",
        "eponym_id", sa.Integer(), sa.ForeignKey("eponym.id"), nullable=True)
    op.drop_constraint("tablet_ibfk_10", "tablet", type="unique")
    op.drop_column("tablet", "year_id")
    