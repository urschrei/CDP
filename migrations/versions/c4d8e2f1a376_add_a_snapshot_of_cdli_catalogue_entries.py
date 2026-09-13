"""Add a snapshot of the CDLI catalogue entries of the tablets

Revision ID: c4d8e2f1a376
Revises: b3f7c1d9e245
Create Date: 2026-09-14 14:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "c4d8e2f1a376"
down_revision = "b3f7c1d9e245"
branch_labels = None
depends_on = None


def upgrade():
    # The table is empty until the next "cdpp import-cdli".
    op.create_table(
        "cdli_artifact",
        sa.Column("tablet_id", sa.Integer(), nullable=False),
        sa.Column("p_number", sa.String(length=12), nullable=False),
        sa.Column("designation", sa.String(length=500), nullable=False),
        sa.Column("museum_no", sa.String(length=500), nullable=True),
        sa.Column("accession_no", sa.String(length=500), nullable=True),
        sa.Column("primary_publication", sa.String(length=500), nullable=True),
        sa.Column("publication_history", sa.String(length=2000), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["tablet_id"],
            ["tablet.id"],
            name=op.f("fk_cdli_artifact_tablet_id_tablet"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_cdli_artifact")),
        sa.UniqueConstraint(
            "tablet_id", "p_number", name=op.f("uq_cdli_artifact_tablet_id")
        ),
    )
    with op.batch_alter_table("cdli_artifact", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_cdli_artifact_tablet_id"), ["tablet_id"], unique=False
        )


def downgrade():
    with op.batch_alter_table("cdli_artifact", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_cdli_artifact_tablet_id"))
    op.drop_table("cdli_artifact")
