"""allow blank locality

Revision ID: 1474a7665ab0
Revises: 1008962986b7
Create Date: 2012-05-24 16:27:34.583977

"""

# revision identifiers, used by Alembic.
revision = '1474a7665ab0'
down_revision = '1008962986b7'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.alter_column('city', 'locality_id', nullable=True, existing_type=sa.Integer())


def downgrade():
    op.alter_column('city', 'locality_id', nullable=False, existing_type=sa.Integer())
