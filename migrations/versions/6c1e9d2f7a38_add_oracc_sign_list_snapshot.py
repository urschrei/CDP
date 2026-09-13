"""Add a snapshot of the Oracc Sign List, and the Oracc name of each sign list

Revision ID: 6c1e9d2f7a38
Revises: b5f0c3a9e214
Create Date: 2026-09-13 14:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "6c1e9d2f7a38"
down_revision = "b5f0c3a9e214"
branch_labels = None
depends_on = None

# The abbreviations that the Oracc Sign List uses for the sign lists of the
# CDP. SLLHA is one numbering for Deimel's Sumerisches Lexikon, Labat's Manuel
# and the Handbuch Assur; the match with the HA and Labat columns is
# provisional. See docs/schema-and-data-questions.md.
ORACC_LISTS = {
    "MesZL": "MZL",
    "ELLes": "ELLES",
    "ZATU": "ZATU",
    "LAK": "LAK",
    "RSP": "RSP",
    "HZL": "HZL",
    "HA": "SLLHA",
    "aBZL": "ABZL",
    "REC": "REC",
    "Labat": "SLLHA",
    "KWU": "KWU",
}


def upgrade():
    op.create_table(
        "oracc_sign",
        sa.Column("oid", sa.String(length=12), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("ebl_url", sa.String(length=500), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_oracc_sign")),
        sa.UniqueConstraint("oid", name=op.f("uq_oracc_sign_oid")),
    )
    with op.batch_alter_table("oracc_sign", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_oracc_sign_name"), ["name"], unique=False)

    op.create_table(
        "oracc_list_number",
        sa.Column("oracc_sign_id", sa.Integer(), nullable=False),
        sa.Column("list_name", sa.String(length=20), nullable=False),
        sa.Column("number", sa.String(length=50), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["oracc_sign_id"],
            ["oracc_sign.id"],
            name=op.f("fk_oracc_list_number_oracc_sign_id_oracc_sign"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_oracc_list_number")),
        sa.UniqueConstraint(
            "oracc_sign_id",
            "list_name",
            "number",
            name=op.f("uq_oracc_list_number_oracc_sign_id"),
        ),
    )
    with op.batch_alter_table("oracc_list_number", schema=None) as batch_op:
        batch_op.create_index(
            "ix_oracc_list_number_list_name_number",
            ["list_name", "number"],
            unique=False,
        )
        batch_op.create_index(
            batch_op.f("ix_oracc_list_number_oracc_sign_id"),
            ["oracc_sign_id"],
            unique=False,
        )

    with op.batch_alter_table("sign_list", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("oracc_list", sa.String(length=20), nullable=True)
        )

    sign_list = sa.table("sign_list", sa.column("name"), sa.column("oracc_list"))
    for name, oracc_list in ORACC_LISTS.items():
        op.execute(
            sign_list.update()
            .where(sign_list.c.name == name)
            .values(oracc_list=oracc_list)
        )


def downgrade():
    with op.batch_alter_table("sign_list", schema=None) as batch_op:
        batch_op.drop_column("oracc_list")

    with op.batch_alter_table("oracc_list_number", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_oracc_list_number_oracc_sign_id"))
        batch_op.drop_index("ix_oracc_list_number_list_name_number")

    op.drop_table("oracc_list_number")

    with op.batch_alter_table("oracc_sign", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_oracc_sign_name"))

    op.drop_table("oracc_sign")
