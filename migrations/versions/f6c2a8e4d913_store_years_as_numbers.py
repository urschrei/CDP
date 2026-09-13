"""Store years as numbers

Revision ID: f6c2a8e4d913
Revises: e3b9d1f7a520
Create Date: 2026-09-13 18:00:00.000000

Years are integers in astronomical numbering: 1 BC is 0, and 1244 BC is -1243.
The table year had a row for each year from 2400 BC to 200 AD. The table
eponym_year keeps only the years that have an eponym.
"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "f6c2a8e4d913"
down_revision = "e3b9d1f7a520"
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
FORMER_TABLET_YEAR_EPONYM = (
    "tablet_year_eponym",
    "tablet",
    ("year_id", "eponym_id"),
    ("INSERT", "UPDATE"),
    "NEW.eponym_id IS NOT NULL"
    " AND (SELECT eponym_id FROM year WHERE id = NEW.year_id) IS NOT NULL"
    " AND NEW.eponym_id IS NOT (SELECT eponym_id FROM year WHERE id = NEW.year_id)",
    "A tablet must have the eponym of its year.",
)
FORMER_YEAR_EPONYM = (
    "year_eponym",
    "year",
    ("eponym_id",),
    ("UPDATE",),
    "NEW.eponym_id IS NOT NULL AND EXISTS (SELECT 1 FROM tablet"
    " WHERE year_id = NEW.id AND eponym_id IS NOT NULL"
    " AND eponym_id IS NOT NEW.eponym_id)",
    "A year must have the eponym of its tablets.",
)
TABLET_YEAR_EPONYM = (
    "tablet_year_eponym",
    "tablet",
    ("year", "eponym_id"),
    ("INSERT", "UPDATE"),
    "NEW.eponym_id IS NOT NULL AND EXISTS (SELECT 1 FROM eponym_year"
    " WHERE year = NEW.year AND eponym_id IS NOT NEW.eponym_id)",
    "A tablet must have the eponym of its year.",
)
YEAR_EPONYM = (
    "year_eponym",
    "eponym_year",
    ("year", "eponym_id"),
    ("INSERT", "UPDATE"),
    "EXISTS (SELECT 1 FROM tablet WHERE year = NEW.year"
    " AND eponym_id IS NOT NULL AND eponym_id IS NOT NEW.eponym_id)",
    "A year must have the eponym of its tablets.",
)
BEFORE = (
    TABLET_SUB_PERIOD,
    REIGN_SUB_PERIOD,
    FORMER_TABLET_YEAR_EPONYM,
    SUB_PERIOD_PERIOD,
    FORMER_YEAR_EPONYM,
)
AFTER = (
    TABLET_SUB_PERIOD,
    REIGN_SUB_PERIOD,
    TABLET_YEAR_EPONYM,
    SUB_PERIOD_PERIOD,
    YEAR_EPONYM,
)
# The former table year numbered 1 BC to 2400 BC first, then 1 AD to 200 AD.
FIRST_YEAR = -2399
LAST_YEAR = 200


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


def year_number(column):
    """Return SQL that converts a year such as "1244 BC" to its number, -1243."""
    digits = f"CAST(substr({column}, 1, instr({column}, ' ') - 1) AS INTEGER)"
    return f"CASE WHEN {column} LIKE '% BC' THEN 1 - {digits} ELSE {digits} END"


def year_text(column):
    """Return SQL that converts a year number such as -1243 to "1244 BC"."""
    return (
        f"CASE WHEN {column} <= 0 THEN (1 - {column}) || ' BC'"
        f" ELSE {column} || ' AD' END"
    )


def upgrade():
    connection = op.get_bind()
    for table, column in (
        ("year", "year"),
        ("period", "from_date"),
        ("period", "to_date"),
    ):
        others = connection.scalar(
            sa.text(
                f"SELECT count(*) FROM {table} WHERE {column} NOT GLOB '[1-9]* BC'"
                f" AND {column} NOT GLOB '[1-9]* AD'"
            )
        )
        if others:
            raise RuntimeError(
                f"{others} values of {table}.{column} are not years such as 1244 BC."
            )
    drop_triggers(BEFORE)

    op.create_table(
        "eponym_year",
        sa.Column("year", sa.Integer(), autoincrement=False, nullable=False),
        sa.Column("eponym_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["eponym_id"],
            ["eponym.id"],
            name=op.f("fk_eponym_year_eponym_id_eponym"),
        ),
        sa.PrimaryKeyConstraint("year", name=op.f("pk_eponym_year")),
    )
    op.create_index(
        op.f("ix_eponym_year_eponym_id"), "eponym_year", ["eponym_id"], unique=False
    )
    op.execute(
        f"INSERT INTO eponym_year (year, eponym_id) SELECT {year_number('year')},"
        " eponym_id FROM year WHERE eponym_id IS NOT NULL"
    )

    op.add_column("tablet", sa.Column("year", sa.Integer(), nullable=True))
    op.execute(
        "UPDATE tablet SET year ="
        f" (SELECT {year_number('y.year')} FROM year y WHERE y.id = tablet.year_id)"
    )
    # Batch mode makes each table again, so it removes the triggers of the table.
    with op.batch_alter_table("tablet", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_tablet_year_id"))
        batch_op.drop_constraint(
            batch_op.f("fk_tablet_year_id_year"), type_="foreignkey"
        )
        batch_op.drop_column("year_id")

    for end in ("start", "end"):
        op.add_column("reign", sa.Column(f"{end}_year", sa.Integer(), nullable=True))
        op.execute(
            f"UPDATE reign SET {end}_year = (SELECT {year_number('y.year')}"
            f" FROM year y WHERE y.id = reign.{end}_date)"
        )
    with op.batch_alter_table("reign", schema=None) as batch_op:
        for end in ("start", "end"):
            batch_op.drop_index(batch_op.f(f"ix_reign_{end}_date"))
            batch_op.drop_constraint(
                batch_op.f(f"fk_reign_{end}_date_year"), type_="foreignkey"
            )
            batch_op.drop_column(f"{end}_date")

    op.add_column("period", sa.Column("start_year", sa.Integer(), nullable=True))
    op.add_column("period", sa.Column("end_year", sa.Integer(), nullable=True))
    op.execute(
        f"UPDATE period SET start_year = {year_number('from_date')},"
        f" end_year = {year_number('to_date')}"
    )
    with op.batch_alter_table("period", schema=None) as batch_op:
        batch_op.drop_column("from_date")
        batch_op.drop_column("to_date")

    op.drop_table("year")
    create_triggers(AFTER)


def downgrade():
    connection = op.get_bind()
    drop_triggers(AFTER)

    op.create_table(
        "year",
        sa.Column("year", sa.String(length=14), nullable=False),
        sa.Column("eponym_id", sa.Integer(), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["eponym_id"], ["eponym.id"], name=op.f("fk_year_eponym_id_eponym")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_year")),
        sa.UniqueConstraint("year", name=op.f("uq_year_year")),
    )
    op.create_index(op.f("ix_year_eponym_id"), "year", ["eponym_id"], unique=False)
    used_first, used_last = connection.execute(
        sa.text(
            "SELECT min(year), max(year) FROM (SELECT year FROM tablet"
            " UNION SELECT start_year FROM reign UNION SELECT end_year FROM reign"
            " UNION SELECT year FROM eponym_year)"
        )
    ).one()
    first = min(FIRST_YEAR, FIRST_YEAR if used_first is None else used_first)
    last = max(LAST_YEAR, LAST_YEAR if used_last is None else used_last)
    numbers = [*range(0, first - 1, -1), *range(1, last + 1)]
    connection.execute(
        sa.text("INSERT INTO year (id, year) VALUES (:id, :year)"),
        [
            {"id": index, "year": f"{1 - number} BC" if number <= 0 else f"{number} AD"}
            for index, number in enumerate(numbers, start=1)
        ],
    )
    op.execute(
        "UPDATE year SET eponym_id = (SELECT eponym_id FROM eponym_year e"
        f" WHERE e.year = {year_number('year.year')})"
    )

    op.add_column("tablet", sa.Column("year_id", sa.Integer(), nullable=True))
    op.execute(
        "UPDATE tablet SET year_id ="
        f" (SELECT id FROM year y WHERE y.year = {year_text('tablet.year')})"
    )
    with op.batch_alter_table("tablet", schema=None) as batch_op:
        batch_op.create_foreign_key(
            batch_op.f("fk_tablet_year_id_year"), "year", ["year_id"], ["id"]
        )
        batch_op.create_index(
            batch_op.f("ix_tablet_year_id"), ["year_id"], unique=False
        )
        batch_op.drop_column("year")

    for end in ("start", "end"):
        op.add_column("reign", sa.Column(f"{end}_date", sa.Integer(), nullable=True))
        op.execute(
            f"UPDATE reign SET {end}_date = (SELECT id FROM year y"
            f" WHERE y.year = {year_text(f'reign.{end}_year')})"
        )
    with op.batch_alter_table("reign", schema=None) as batch_op:
        for end in ("start", "end"):
            batch_op.create_foreign_key(
                batch_op.f(f"fk_reign_{end}_date_year"), "year", [f"{end}_date"], ["id"]
            )
            batch_op.create_index(
                batch_op.f(f"ix_reign_{end}_date"), [f"{end}_date"], unique=False
            )
            batch_op.drop_column(f"{end}_year")

    op.add_column("period", sa.Column("from_date", sa.String(length=50), nullable=True))
    op.add_column("period", sa.Column("to_date", sa.String(length=50), nullable=True))
    op.execute(
        f"UPDATE period SET from_date = coalesce({year_text('start_year')}, ''),"
        f" to_date = coalesce({year_text('end_year')}, '')"
    )
    with op.batch_alter_table("period", schema=None) as batch_op:
        batch_op.alter_column(
            "from_date", existing_type=sa.String(length=50), nullable=False
        )
        batch_op.alter_column(
            "to_date", existing_type=sa.String(length=50), nullable=False
        )
        batch_op.drop_column("start_year")
        batch_op.drop_column("end_year")

    op.drop_table("eponym_year")
    create_triggers(BEFORE)
