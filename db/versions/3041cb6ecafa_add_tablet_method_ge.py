"""Add tablet method genre function

Revision ID: 3041cb6ecafa
Revises: 1f48027357c
Create Date: 2012-05-28 23:55:22.661300

"""

# revision identifiers, used by Alembic.
revision = '3041cb6ecafa'
down_revision = '1f48027357c'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column("tablet",
        sa.Column("method_id", sa.Integer(), sa.ForeignKey("method.id"), nullable=True))
    op.add_column("tablet",
        sa.Column("function_id", sa.Integer(), sa.ForeignKey("function.id"), nullable=True))
    op.add_column("tablet",
        sa.Column("genre_id", sa.Integer(), sa.ForeignKey("genre.id"), nullable=True))


def downgrade():
    op.drop_constraint("tablet_ibfk_11", "tablet", type="foreignkey")
    op.drop_constraint("tablet_ibfk_12", "tablet", type="foreignkey")
    op.drop_constraint("tablet_ibfk_13", "tablet", type="foreignkey")
    op.drop_column("tablet", "method_id")
    op.drop_column("tablet", "function_id")
    op.drop_column("tablet", "genre_id")