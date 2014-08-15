"""Ensure Sign tables are unique and non-nullable

Revision ID: b0de4bc6da1
Revises: 1fc04d3ee8c2
Create Date: 2014-08-14 16:13:25.459709

"""

# revision identifiers, used by Alembic.
revision = 'b0de4bc6da1'
down_revision = '1fc04d3ee8c2'

from alembic import op
import sqlalchemy as sa


def upgrade():
    # op.alter_column("Sign", "sign_ref", existing_type=sa.String(150), nullable=False, unique=True)
    op.create_unique_constraint('uq_sign_ref', "Sign", ["sign_ref"])
    op.create_unique_constraint('uq_sign_ref', "Oracc", ["sign_ref"])
    op.create_unique_constraint('uq_sign_ref', "Cdli", ["sign_ref"])
    op.create_unique_constraint('uq_sign_ref', "Description", ["sign_ref"])

def downgrade():
    op.drop_constraint('sign_ref', "Sign", type_='unique')
    op.drop_constraint('sign_ref', "Oracc", type_='unique')
    op.drop_constraint('sign_ref', "Cdli", type_='unique')
    op.drop_constraint('sign_ref', "Description", type_='unique')
