"""adding instance table

Revision ID: 4eb053a8df5f
Revises: 26452a8a6191
Create Date: 2012-06-21 17:08:56.384400

"""

# revision identifiers, used by Alembic.
revision = '4eb053a8df5f'
down_revision = '26452a8a6191'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        "instance",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("sign_id", sa.Integer(), sa.ForeignKey("sign.id"), nullable=False),
        sa.Column("surface_id", sa.Integer(), sa.ForeignKey("surface.id"), nullable=True),
        sa.Column("column_id", sa.Integer(), sa.ForeignKey("column.id"), nullable=True),
        sa.Column("line_id", sa.Integer(), sa.ForeignKey("line.id"), nullable=True),
        sa.Column("function_id", sa.Integer(), sa.ForeignKey("function.id"), nullable=True),
        sa.Column("iteration_id", sa.Integer(), sa.ForeignKey("iteration.id"), nullable=True))


def downgrade():
    op.drop_table("instance")
