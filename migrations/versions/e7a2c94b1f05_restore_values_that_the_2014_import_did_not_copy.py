"""Restore the sign-list numbers, variant names and form descriptions that the
2014 import did not copy

Revision ID: e7a2c94b1f05
Revises: 6c1e9d2f7a38
Create Date: 2026-09-13 16:00:00.000000

"""

import csv
from pathlib import Path

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "e7a2c94b1f05"
down_revision = "6c1e9d2f7a38"
branch_labels = None
depends_on = None

# utils/restore_2013_values.py writes these files from the MySQL dump of
# 22 May 2013. See docs/schema-and-data-questions.md.
DATA = Path(__file__).parents[1] / "data"
ENTRIES_FILE = DATA / "2013_sign_list_entries.csv"
DETAILS_FILE = DATA / "2013_record_details.csv"

cdp = sa.table(
    "cdp", sa.column("id"), sa.column("variant_name"), sa.column("form_description")
)
sign_list = sa.table("sign_list", sa.column("id"), sa.column("name"))
sign_list_entry = sa.table(
    "sign_list_entry",
    sa.column("cdp_id"),
    sa.column("sign_list_id"),
    sa.column("number"),
)


def read_csv(path):
    with path.open(encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def sign_list_ids(bind):
    query = sa.select(sign_list.c.name, sign_list.c.id)
    return {name: list_id for name, list_id in bind.execute(query)}


def upgrade():
    bind = op.get_bind()
    list_ids = sign_list_ids(bind)
    # A database without the CDP records, for example a new database, gets no
    # values.
    record_ids = set(bind.scalars(sa.select(cdp.c.id)))

    entries = [
        {
            "cdp_id": int(row["cdp_id"]),
            "sign_list_id": list_ids[row["sign_list"]],
            "number": row["number"],
        }
        for row in read_csv(ENTRIES_FILE)
        if int(row["cdp_id"]) in record_ids
    ]
    if entries:
        op.bulk_insert(sign_list_entry, entries)

    details = [
        {
            "record_id": int(row["cdp_id"]),
            "variant": row["variant_name"] or None,
            "description": row["form_description"] or None,
        }
        for row in read_csv(DETAILS_FILE)
        if int(row["cdp_id"]) in record_ids
    ]
    if details:
        bind.execute(
            cdp.update()
            .where(cdp.c.id == sa.bindparam("record_id"))
            .values(
                variant_name=sa.bindparam("variant"),
                form_description=sa.bindparam("description"),
            ),
            details,
        )


def downgrade():
    bind = op.get_bind()
    list_ids = sign_list_ids(bind)

    entries = [
        {"record_id": int(row["cdp_id"]), "list_id": list_ids[row["sign_list"]]}
        for row in read_csv(ENTRIES_FILE)
    ]
    bind.execute(
        sign_list_entry.delete().where(
            sign_list_entry.c.cdp_id == sa.bindparam("record_id"),
            sign_list_entry.c.sign_list_id == sa.bindparam("list_id"),
        ),
        entries,
    )

    details = [{"record_id": int(row["cdp_id"])} for row in read_csv(DETAILS_FILE)]
    bind.execute(
        cdp.update()
        .where(cdp.c.id == sa.bindparam("record_id"))
        .values(variant_name=None, form_description=None),
        details,
    )
