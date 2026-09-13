"""Merge the city Alalah into Alalakh, and remove the spaces at the ends of
ruler names

Revision ID: c9b4e2a7d613
Revises: a3d5f8e1c702
Create Date: 2026-09-13 18:30:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "c9b4e2a7d613"
down_revision = "a3d5f8e1c702"
branch_labels = None
depends_on = None

# The columns that refer to a city.
CITY_COLUMNS = (
    ("tablet", "city_id"),
    ("tablet", "origin_city_id"),
    ("reign", "city_id"),
    ("city_site", "city_id"),
)
# Before the merge, these tablets and reigns referred to Alalah.
ALALAH_TABLETS = (
    "BM_130738",
    "BM_131447",
    "BM_131463",
    "BM_131477",
    "BM_131505",
    "BM_131506",
)
ALALAH_REIGNS = ("E.4.34.1", "E.4.34.2", "E.4.34.3")
# Before the change, each of these ruler names had one space at the end.
PADDED_RULERS = (
    "Abi-eshuh",
    "Ashurnasirpal I",
    "Assur-narari IV",
    "Ilu-shumma",
    "Tikulti-Ninurta II",
)


def city_id(bind, name):
    query = sa.text("SELECT id FROM city WHERE name = :name")
    return bind.execute(query, {"name": name}).scalar_one_or_none()


def in_list(sql, name):
    return sa.text(sql).bindparams(sa.bindparam(name, expanding=True))


def upgrade():
    bind = op.get_bind()
    alalah = city_id(bind, "Alalah")
    alalakh = city_id(bind, "Alalakh")
    # A database without the two cities, for example a new database, has
    # nothing to merge.
    if alalah is not None and alalakh is not None:
        for table, column in CITY_COLUMNS:
            bind.execute(
                sa.text(f"UPDATE {table} SET {column} = :new WHERE {column} = :old"),
                {"new": alalakh, "old": alalah},
            )
        bind.execute(sa.text("DELETE FROM city WHERE id = :id"), {"id": alalah})

    op.execute("UPDATE ruler SET name = trim(name) WHERE name != trim(name)")


def downgrade():
    bind = op.get_bind()
    bind.execute(
        in_list("UPDATE ruler SET name = name || ' ' WHERE name IN :names", "names"),
        {"names": list(PADDED_RULERS)},
    )

    if city_id(bind, "Alalakh") is None:
        return
    bind.execute(sa.text("INSERT INTO city (name) VALUES ('Alalah')"))
    alalah = city_id(bind, "Alalah")
    bind.execute(
        in_list(
            "UPDATE tablet SET city_id = :city WHERE museum_number IN :numbers",
            "numbers",
        ),
        {"city": alalah, "numbers": list(ALALAH_TABLETS)},
    )
    bind.execute(
        in_list("UPDATE reign SET city_id = :city WHERE rim_ref IN :refs", "refs"),
        {"city": alalah, "refs": list(ALALAH_REIGNS)},
    )
