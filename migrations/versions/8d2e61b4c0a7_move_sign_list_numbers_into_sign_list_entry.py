"""Move sign-list numbers from cdp columns into sign_list and sign_list_entry

Revision ID: 8d2e61b4c0a7
Revises: 4143f0482f76
Create Date: 2026-09-13 12:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "8d2e61b4c0a7"
down_revision = "4143f0482f76"
branch_labels = None
depends_on = None

# The former cdp columns, in display order. The name of each sign list is the
# column name, with spaces in place of underscores.
SIGN_LIST_COLUMNS = (
    "MesZL",
    "ELLes",
    "ZATU",
    "LAK",
    "UET_2",
    "ARM_XV",
    "Hinke",
    "Clay_BE_A_14",
    "Koenig_AfO_Bei_16",
    "Ranke_BE_A_61",
    "Schroeder_VS_12",
    "Clay_BE_A_10",
    "RSP",
    "Emar",
    "Schroder_VS_15",
    "HZL",
    "HA",
    "aBZL",
    "REC",
    "Labat",
    "KWU",
    "Fossey_pp",
)


def upgrade():
    sign_list = op.create_table(
        "sign_list",
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_sign_list")),
        sa.UniqueConstraint("name", name=op.f("uq_sign_list_name")),
        sa.UniqueConstraint("position", name=op.f("uq_sign_list_position")),
    )
    op.bulk_insert(
        sign_list,
        [
            {"id": position, "name": column.replace("_", " "), "position": position}
            for position, column in enumerate(SIGN_LIST_COLUMNS, start=1)
        ],
    )
    op.create_table(
        "sign_list_entry",
        sa.Column("cdp_id", sa.Integer(), nullable=False),
        sa.Column("sign_list_id", sa.Integer(), nullable=False),
        sa.Column("number", sa.String(length=50), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["cdp_id"],
            ["cdp.id"],
            name=op.f("fk_sign_list_entry_cdp_id_cdp"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["sign_list_id"],
            ["sign_list.id"],
            name=op.f("fk_sign_list_entry_sign_list_id_sign_list"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_sign_list_entry")),
        sa.UniqueConstraint(
            "cdp_id", "sign_list_id", name=op.f("uq_sign_list_entry_cdp_id")
        ),
    )
    with op.batch_alter_table("sign_list_entry", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_sign_list_entry_cdp_id"), ["cdp_id"], unique=False
        )
        batch_op.create_index(
            batch_op.f("ix_sign_list_entry_sign_list_id"),
            ["sign_list_id"],
            unique=False,
        )

    # Copy each value that is not empty. Three KWU values have spaces at the
    # ends, which trim removes.
    for position, column in enumerate(SIGN_LIST_COLUMNS, start=1):
        op.execute(
            "INSERT INTO sign_list_entry (cdp_id, sign_list_id, number) "
            f'SELECT id, {position}, trim("{column}") FROM cdp '
            f"WHERE trim(\"{column}\") != ''"
        )

    with op.batch_alter_table("cdp", schema=None) as batch_op:
        for column in SIGN_LIST_COLUMNS:
            batch_op.drop_column(column)


def downgrade():
    with op.batch_alter_table("cdp", schema=None) as batch_op:
        for column in SIGN_LIST_COLUMNS:
            batch_op.add_column(sa.Column(column, sa.String(length=50), nullable=True))

    for position, column in enumerate(SIGN_LIST_COLUMNS, start=1):
        op.execute(
            f'UPDATE cdp SET "{column}" = (SELECT number FROM sign_list_entry '
            "WHERE sign_list_entry.cdp_id = cdp.id "
            f"AND sign_list_entry.sign_list_id = {position})"
        )

    with op.batch_alter_table("sign_list_entry", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_sign_list_entry_sign_list_id"))
        batch_op.drop_index(batch_op.f("ix_sign_list_entry_cdp_id"))

    op.drop_table("sign_list_entry")
    op.drop_table("sign_list")
