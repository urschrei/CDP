"""Add a snapshot of the Oracc texts of the tablets

Revision ID: e5a1c7d3f920
Revises: c4d8e2f1a376
Create Date: 2026-09-14 16:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "e5a1c7d3f920"
down_revision = "c4d8e2f1a376"
branch_labels = None
depends_on = None


def upgrade():
    # The table is empty until the next "cdpp import-oracc-texts".
    op.create_table(
        "oracc_text",
        sa.Column("tablet_id", sa.Integer(), nullable=False),
        sa.Column("project", sa.String(length=50), nullable=False),
        sa.Column("text_id", sa.String(length=12), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["tablet_id"],
            ["tablet.id"],
            name=op.f("fk_oracc_text_tablet_id_tablet"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_oracc_text")),
        sa.UniqueConstraint(
            "tablet_id", "project", "text_id", name=op.f("uq_oracc_text_tablet_id")
        ),
    )
    with op.batch_alter_table("oracc_text", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_oracc_text_tablet_id"), ["tablet_id"], unique=False
        )


def downgrade():
    with op.batch_alter_table("oracc_text", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_oracc_text_tablet_id"))
    op.drop_table("oracc_text")
