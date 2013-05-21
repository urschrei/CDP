"""Make CDP columns case-sensitive

Revision ID: 3bfb6c150903
Revises: 1bb7ffca76ba
Create Date: 2013-05-21 17:43:49.886947

"""

# revision identifiers, used by Alembic.
revision = '3bfb6c150903'
down_revision = '1bb7ffca76ba'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.alter_column(
        table_name="Cdp",
        column_name="sign_ref",
        type_=sa.dialects.mysql.VARCHAR(150, collation='utf8_bin'),
        existing_type=sa.String(150))


def downgrade():
    op.alter_column(
        table_name="Cdp",
        column_name="sign_ref",
        type_=sa.String(150),
        existing_type=sa.String(150))
