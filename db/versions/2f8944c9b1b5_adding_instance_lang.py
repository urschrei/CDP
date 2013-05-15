"""adding instance-language association table

Revision ID: 2f8944c9b1b5
Revises: 37d8aa5e5237
Create Date: 2012-06-29 22:31:39.751057

"""

# revision identifiers, used by Alembic.
revision = '2f8944c9b1b5'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    instance_language = op.create_table(
        "instance_language",
        sa.Column("instance_id", sa.Integer(), sa.ForeignKey("instance.id"), nullable=False),
        sa.Column("language_id", sa.Integer(), sa.ForeignKey("language.id"), nullable=False))


def downgrade():
    op.drop_table("instance_language")