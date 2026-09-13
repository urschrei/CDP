"""Take the locality of a tablet from its city

Revision ID: e3b9d1f7a520
Revises: d8a1f3c5e742
Create Date: 2026-09-13 17:00:00.000000

A tablet with a city has no locality of its own. The check constraint
ck_tablet_city_or_locality replaces the triggers that kept the locality of a
tablet the same as the locality of its city.
"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "e3b9d1f7a520"
down_revision = "d8a1f3c5e742"
branch_labels = None
depends_on = None

# The consistency rules before and after this migration. See
# cdpp.models.CONSISTENCY_RULES.
TABLET_SUB_PERIOD = (
    "tablet_sub_period",
    "tablet",
    ("period_id", "sub_period_id"),
    ("INSERT", "UPDATE"),
    "NEW.sub_period_id IS NOT NULL AND NEW.period_id IS NOT"
    " (SELECT period_id FROM sub_period WHERE id = NEW.sub_period_id)",
    "The sub-period of a tablet must belong to the period of the tablet.",
)
REIGN_SUB_PERIOD = (
    "reign_sub_period",
    "reign",
    ("period_id", "sub_period_id"),
    ("INSERT", "UPDATE"),
    "NEW.sub_period_id IS NOT NULL AND NEW.period_id IS NOT"
    " (SELECT period_id FROM sub_period WHERE id = NEW.sub_period_id)",
    "The sub-period of a reign must belong to the period of the reign.",
)
TABLET_CITY_LOCALITY = (
    "tablet_city_locality",
    "tablet",
    ("city_id", "locality_id"),
    ("INSERT", "UPDATE"),
    "(SELECT locality_id FROM city WHERE id = NEW.city_id) IS NOT NULL"
    " AND NEW.locality_id IS NOT"
    " (SELECT locality_id FROM city WHERE id = NEW.city_id)",
    "A tablet must have the locality of its city.",
)
TABLET_YEAR_EPONYM = (
    "tablet_year_eponym",
    "tablet",
    ("year_id", "eponym_id"),
    ("INSERT", "UPDATE"),
    "NEW.eponym_id IS NOT NULL"
    " AND (SELECT eponym_id FROM year WHERE id = NEW.year_id) IS NOT NULL"
    " AND NEW.eponym_id IS NOT (SELECT eponym_id FROM year WHERE id = NEW.year_id)",
    "A tablet must have the eponym of its year.",
)
SUB_PERIOD_PERIOD = (
    "sub_period_period",
    "sub_period",
    ("period_id",),
    ("UPDATE",),
    "EXISTS (SELECT 1 FROM tablet"
    " WHERE sub_period_id = NEW.id AND period_id IS NOT NEW.period_id)"
    " OR EXISTS (SELECT 1 FROM reign"
    " WHERE sub_period_id = NEW.id AND period_id IS NOT NEW.period_id)",
    "A sub-period must have the period of its tablets and reigns.",
)
CITY_LOCALITY = (
    "city_locality",
    "city",
    ("locality_id",),
    ("UPDATE",),
    "NEW.locality_id IS NOT NULL AND EXISTS (SELECT 1 FROM tablet"
    " WHERE city_id = NEW.id AND locality_id IS NOT NEW.locality_id)",
    "A city must have the locality of its tablets.",
)
YEAR_EPONYM = (
    "year_eponym",
    "year",
    ("eponym_id",),
    ("UPDATE",),
    "NEW.eponym_id IS NOT NULL AND EXISTS (SELECT 1 FROM tablet"
    " WHERE year_id = NEW.id AND eponym_id IS NOT NULL"
    " AND eponym_id IS NOT NEW.eponym_id)",
    "A year must have the eponym of its tablets.",
)
BEFORE = (
    TABLET_SUB_PERIOD,
    REIGN_SUB_PERIOD,
    TABLET_CITY_LOCALITY,
    TABLET_YEAR_EPONYM,
    SUB_PERIOD_PERIOD,
    CITY_LOCALITY,
    YEAR_EPONYM,
)
AFTER = (
    TABLET_SUB_PERIOD,
    REIGN_SUB_PERIOD,
    TABLET_YEAR_EPONYM,
    SUB_PERIOD_PERIOD,
    YEAR_EPONYM,
)
CONSTRAINT = "ck_tablet_city_or_locality"


def triggers(rules):
    for name, table, columns, statements, condition, message in rules:
        for statement in statements:
            timing = (
                statement
                if statement == "INSERT"
                else f"UPDATE OF {', '.join(columns)}"
            )
            yield (
                f"{name}_{statement.lower()}",
                f"CREATE TRIGGER {name}_{statement.lower()} BEFORE {timing}"
                f" ON {table} FOR EACH ROW WHEN {condition}"
                f" BEGIN SELECT RAISE(ABORT, '{name}: {message}'); END",
            )


def drop_triggers(rules):
    for name, _ in triggers(rules):
        op.execute(f"DROP TRIGGER IF EXISTS {name}")


def create_triggers(rules):
    for _, statement in triggers(rules):
        op.execute(statement)


def upgrade():
    different = op.get_bind().scalar(
        sa.text(
            "SELECT count(*) FROM tablet t JOIN city c ON c.id = t.city_id"
            " WHERE t.locality_id IS NOT NULL AND t.locality_id IS NOT c.locality_id"
        )
    )
    if different:
        raise RuntimeError(
            f"{different} tablets have a locality that is not the locality of their "
            "city. Correct them before this migration removes the localities of "
            "tablets with a city."
        )
    drop_triggers(BEFORE)
    op.execute("UPDATE tablet SET locality_id = NULL WHERE city_id IS NOT NULL")
    # Batch mode makes the table again, so it removes the triggers of the table.
    with op.batch_alter_table("tablet", schema=None) as batch_op:
        batch_op.create_check_constraint(
            op.f(CONSTRAINT), "city_id IS NULL OR locality_id IS NULL"
        )
    create_triggers(AFTER)


def downgrade():
    drop_triggers(AFTER)
    with op.batch_alter_table("tablet", schema=None) as batch_op:
        batch_op.drop_constraint(op.f(CONSTRAINT), type_="check")
    op.execute(
        "UPDATE tablet SET locality_id ="
        " (SELECT locality_id FROM city WHERE id = tablet.city_id)"
        " WHERE city_id IS NOT NULL"
    )
    create_triggers(BEFORE)
