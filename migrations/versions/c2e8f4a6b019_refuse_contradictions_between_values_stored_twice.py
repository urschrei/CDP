"""Refuse contradictions between values that the schema stores twice

Revision ID: c2e8f4a6b019
Revises: 73708b382e0f
Create Date: 2026-09-13 15:00:00.000000

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "c2e8f4a6b019"
down_revision = "73708b382e0f"
branch_labels = None
depends_on = None

# The models create the same triggers. See cdpp.models.CONSISTENCY_RULES.
RULES = (
    (
        "tablet_sub_period",
        "tablet",
        ("period_id", "sub_period_id"),
        ("INSERT", "UPDATE"),
        "NEW.sub_period_id IS NOT NULL AND NEW.period_id IS NOT"
        " (SELECT period_id FROM sub_period WHERE id = NEW.sub_period_id)",
        "The sub-period of a tablet must belong to the period of the tablet.",
    ),
    (
        "reign_sub_period",
        "reign",
        ("period_id", "sub_period_id"),
        ("INSERT", "UPDATE"),
        "NEW.sub_period_id IS NOT NULL AND NEW.period_id IS NOT"
        " (SELECT period_id FROM sub_period WHERE id = NEW.sub_period_id)",
        "The sub-period of a reign must belong to the period of the reign.",
    ),
    (
        "tablet_city_locality",
        "tablet",
        ("city_id", "locality_id"),
        ("INSERT", "UPDATE"),
        "(SELECT locality_id FROM city WHERE id = NEW.city_id) IS NOT NULL"
        " AND NEW.locality_id IS NOT"
        " (SELECT locality_id FROM city WHERE id = NEW.city_id)",
        "A tablet must have the locality of its city.",
    ),
    (
        "tablet_year_eponym",
        "tablet",
        ("year_id", "eponym_id"),
        ("INSERT", "UPDATE"),
        "NEW.eponym_id IS NOT NULL"
        " AND (SELECT eponym_id FROM year WHERE id = NEW.year_id) IS NOT NULL"
        " AND NEW.eponym_id IS NOT (SELECT eponym_id FROM year WHERE id = NEW.year_id)",
        "A tablet must have the eponym of its year.",
    ),
    (
        "sub_period_period",
        "sub_period",
        ("period_id",),
        ("UPDATE",),
        "EXISTS (SELECT 1 FROM tablet"
        " WHERE sub_period_id = NEW.id AND period_id IS NOT NEW.period_id)"
        " OR EXISTS (SELECT 1 FROM reign"
        " WHERE sub_period_id = NEW.id AND period_id IS NOT NEW.period_id)",
        "A sub-period must have the period of its tablets and reigns.",
    ),
    (
        "city_locality",
        "city",
        ("locality_id",),
        ("UPDATE",),
        "NEW.locality_id IS NOT NULL AND EXISTS (SELECT 1 FROM tablet"
        " WHERE city_id = NEW.id AND locality_id IS NOT NEW.locality_id)",
        "A city must have the locality of its tablets.",
    ),
    (
        "year_eponym",
        "year",
        ("eponym_id",),
        ("UPDATE",),
        "NEW.eponym_id IS NOT NULL AND EXISTS (SELECT 1 FROM tablet"
        " WHERE year_id = NEW.id AND eponym_id IS NOT NULL"
        " AND eponym_id IS NOT NEW.eponym_id)",
        "A year must have the eponym of its tablets.",
    ),
)


def triggers():
    for name, table, columns, statements, condition, message in RULES:
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


def upgrade():
    # The triggers do not check the rows that exist. 83-1-18_287 has an eponym
    # that is not the eponym of its year. See docs/schema-and-data-questions.md.
    for _, statement in triggers():
        op.execute(statement)


def downgrade():
    for name, _ in triggers():
        op.execute(f"DROP TRIGGER {name}")
