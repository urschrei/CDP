"""Make CDP sign columns nullable

Revision ID: 1fc04d3ee8c2
Revises: 1e1a5bcdef73
Create Date: 2014-08-14 10:29:38.945298

"""

# revision identifiers, used by Alembic.
revision = '1fc04d3ee8c2'
down_revision = '1e1a5bcdef73'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.alter_column("Cdp", "description_id", existing_type=sa.Integer(), nullable=True)
    op.alter_column("Cdp", "oracc_id", existing_type=sa.Integer(), nullable=True)
    op.alter_column("Cdp", "cdli_id", existing_type=sa.Integer(), nullable=True)


def downgrade():
    op.alter_column("Cdp", "description_id", existing_type=sa.Integer(), nullable=False)
    op.alter_column("Cdp", "oracc_id", existing_type=sa.Integer(), nullable=False)
    op.alter_column("Cdp", "cdli_id", existing_type=sa.Integer(), nullable=False)
