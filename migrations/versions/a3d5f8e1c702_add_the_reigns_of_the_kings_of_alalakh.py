"""Add the reigns of the kings of Alalakh in dynasty B.20

Revision ID: a3d5f8e1c702
Revises: e7a2c94b1f05
Create Date: 2026-09-13 18:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "a3d5f8e1c702"
down_revision = "e7a2c94b1f05"
branch_labels = None
depends_on = None

# The ruler, the RIM reference, the first year and the last year of each reign.
# The notes that came with csvs/ruler_name_matching.xlsx give the numbers and
# the dates.
REIGNS = (
    ("Idrimi", "B.20.1", "1470 BC", None),
    ("Addu-nirari", "B.20.2", None, None),
    ("Niqmepuh", "B.20.3", "1450 BC", "1425 BC"),
    ("Ilim-ilimma II", "B.20.4", "1420 BC", None),
)

reign = sa.table(
    "reign",
    sa.column("ruler_id"),
    sa.column("rim_ref"),
    sa.column("city_id"),
    sa.column("start_date"),
    sa.column("end_date"),
    sa.column("dynasty_id"),
    sa.column("period_id"),
)


def row_id(bind, table, column, value):
    """Return the ID of the row of table whose column holds value, or None."""
    if value is None:
        return None
    query = sa.text(f'SELECT id FROM "{table}" WHERE "{column}" = :value')
    return bind.execute(query, {"value": value}).scalar_one_or_none()


def upgrade():
    bind = op.get_bind()
    dynasty_id = row_id(bind, "dynasty", "name", "B.20")
    # A database without the dynasty, for example a new database, gets no
    # reigns.
    if dynasty_id is None:
        return

    city_id = row_id(bind, "city", "name", "Alalakh")
    period_id = row_id(bind, "period", "name", "Middle Babylonian")
    op.bulk_insert(
        reign,
        [
            {
                "ruler_id": row_id(bind, "ruler", "name", ruler),
                "rim_ref": rim_ref,
                "city_id": city_id,
                "start_date": row_id(bind, "year", "year", first_year),
                "end_date": row_id(bind, "year", "year", last_year),
                "dynasty_id": dynasty_id,
                "period_id": period_id,
            }
            for ruler, rim_ref, first_year, last_year in REIGNS
        ],
    )


def downgrade():
    rim_refs = [rim_ref for _, rim_ref, _, _ in REIGNS]
    op.execute(reign.delete().where(reign.c.rim_ref.in_(rim_refs)))
