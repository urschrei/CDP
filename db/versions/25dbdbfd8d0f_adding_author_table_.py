"""adding author table, and Tablet field

Revision ID: 25dbdbfd8d0f
Revises: 264ba6426b8f
Create Date: 2012-06-19 12:52:20.127419

"""

# revision identifiers, used by Alembic.
revision = '25dbdbfd8d0f'
down_revision = '264ba6426b8f'

from alembic import op
import sqlalchemy as sa


def upgrade():
    author = op.create_table(
        "author",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(75), unique=True, nullable=False))
    op.add_column(
        "Tablet", sa.Column("author_id", sa.Integer(), sa.ForeignKey("author.id"), nullable=True))


