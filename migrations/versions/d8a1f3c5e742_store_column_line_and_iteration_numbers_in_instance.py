"""Store column, line and iteration numbers in the instance table

Revision ID: d8a1f3c5e742
Revises: c2e8f4a6b019
Create Date: 2026-09-13 16:00:00.000000

The upgrade converts the changes that refer to the former lookup records, and
removes the changes that inserted them. The downgrade makes the lookup records
again from the numbers, but not the changes that inserted them.
"""

import json
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "d8a1f3c5e742"
down_revision = "c2e8f4a6b019"
branch_labels = None
depends_on = None

# The lookup table, the reference column and the number column of each
# position. The model attribute, and the field of a change, have the name of
# the lookup table.
POSITIONS = (
    ("column", "column_id", "column_number"),
    ("line", "line_id", "line_number"),
    ("iteration", "iteration_id", "iteration_number"),
)
LOOKUP_TABLES = "('column', 'line', 'iteration')"
# The models create the same triggers. See cdpp.models.append_only.
CHANGE_TRIGGERS = {
    f"change_no_{action.lower()}": (
        f"CREATE TRIGGER change_no_{action.lower()} BEFORE {action} ON change "
        "BEGIN SELECT RAISE(ABORT, 'change rows cannot be changed or deleted'); END"
    )
    for action in ("UPDATE", "DELETE")
}
UPDATE_CHANGE = sa.text(
    "UPDATE change SET field = :field, old_value = :old, new_value = :new"
    " WHERE id = :id"
)


@contextmanager
def changes_can_change() -> Iterator[None]:
    """Remove the triggers of the change table, and make them again after."""
    for name in CHANGE_TRIGGERS:
        op.execute(f"DROP TRIGGER {name}")
    yield
    for statement in CHANGE_TRIGGERS.values():
        op.execute(statement)


def load(value: Any) -> Any:
    # SQLite stores a JSON number in a JSON column as a number, not as text.
    return json.loads(value) if isinstance(value, str) else value


def position_changes(fields: list[str]) -> list[Any]:
    statement = sa.text(
        "SELECT id, field, old_value, new_value FROM change"
        " WHERE table_name = 'instance' AND field IN :fields"
    ).bindparams(sa.bindparam("fields", expanding=True))
    return list(op.get_bind().execute(statement, {"fields": fields}))


def rewrite(
    changes: list[Any], fields: dict[str, str], values: dict[str, dict]
) -> None:
    """Give each change the field in ``fields``, and the values in ``values``."""
    with changes_can_change():
        for change_id, field, old, new in changes:
            op.get_bind().execute(
                UPDATE_CHANGE,
                {
                    "id": change_id,
                    "field": fields[field],
                    "old": json.dumps(values[field].get(load(old))),
                    "new": json.dumps(values[field].get(load(new))),
                },
            )


def upgrade():
    connection = op.get_bind()
    with op.batch_alter_table("instance", schema=None) as batch_op:
        for _, _, number in POSITIONS:
            batch_op.add_column(sa.Column(number, sa.String(length=10), nullable=True))
    for table, reference, number in POSITIONS:
        op.execute(
            f"UPDATE instance SET {number} ="
            f' (SELECT number FROM "{table}" WHERE id = instance.{reference})'
        )

    fields = {reference: table for table, reference, _ in POSITIONS}
    changes = position_changes(list(fields))
    inserts = connection.scalar(
        sa.text(
            "SELECT count(*) FROM change"
            f" WHERE kind = 'insert' AND table_name IN {LOOKUP_TABLES}"
        )
    )
    if changes:
        numbers = {
            reference: dict(
                connection.execute(sa.text(f'SELECT id, number FROM "{table}"')).all()
            )
            for table, reference, _ in POSITIONS
        }
        rewrite(changes, fields, numbers)
    if inserts:
        with changes_can_change():
            op.execute(
                "DELETE FROM change"
                f" WHERE kind = 'insert' AND table_name IN {LOOKUP_TABLES}"
            )

    with op.batch_alter_table("instance", schema=None) as batch_op:
        for table, reference, _ in POSITIONS:
            batch_op.drop_index(batch_op.f(f"ix_instance_{reference}"))
            batch_op.drop_constraint(
                batch_op.f(f"fk_instance_{reference}_{table}"), type_="foreignkey"
            )
            batch_op.drop_column(reference)
    for table, _, _ in POSITIONS:
        op.drop_table(table)


def downgrade():
    connection = op.get_bind()
    fields = {table: reference for table, reference, _ in POSITIONS}
    changes = position_changes(list(fields))
    for table, _, number in POSITIONS:
        op.create_table(
            table,
            sa.Column("number", sa.String(length=5), nullable=False),
            sa.Column("id", sa.Integer(), nullable=False),
            sa.PrimaryKeyConstraint("id", name=op.f(f"pk_{table}")),
            sa.UniqueConstraint("number", name=op.f(f"uq_{table}_number")),
        )
        values = set(
            connection.scalars(
                sa.text(f"SELECT {number} FROM instance WHERE {number} IS NOT NULL")
            )
        )
        for _, field, old, new in changes:
            if field == table:
                values |= {value for value in (load(old), load(new)) if value}
        if values:
            connection.execute(
                sa.text(f'INSERT INTO "{table}" (number) VALUES (:number)'),
                [{"number": value} for value in sorted(values)],
            )

    with op.batch_alter_table("instance", schema=None) as batch_op:
        for table, reference, _ in POSITIONS:
            batch_op.add_column(sa.Column(reference, sa.Integer(), nullable=True))
            batch_op.create_foreign_key(
                batch_op.f(f"fk_instance_{reference}_{table}"),
                table,
                [reference],
                ["id"],
            )
            batch_op.create_index(
                batch_op.f(f"ix_instance_{reference}"), [reference], unique=False
            )
    for table, reference, number in POSITIONS:
        op.execute(
            f"UPDATE instance SET {reference} ="
            f' (SELECT id FROM "{table}" WHERE number = instance.{number})'
        )
    if changes:
        ids = {
            table: {
                number: record_id
                for record_id, number in connection.execute(
                    sa.text(f'SELECT id, number FROM "{table}"')
                )
            }
            for table, _, _ in POSITIONS
        }
        rewrite(changes, fields, ids)

    with op.batch_alter_table("instance", schema=None) as batch_op:
        for _, _, number in POSITIONS:
            batch_op.drop_column(number)
