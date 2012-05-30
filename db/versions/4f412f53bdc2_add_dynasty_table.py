"""Add Dynasty table

Revision ID: 4f412f53bdc2
Revises: 3041cb6ecafa
Create Date: 2012-05-30 14:08:05.779871

"""

# revision identifiers, used by Alembic.
revision = '4f412f53bdc2'
down_revision = '3041cb6ecafa'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        "dynasty",
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False, unique=True))


def downgrade():
    op.drop_table("dynasty")
