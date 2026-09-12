"""Load a MySQL dump of the original CDPP database into the SQLite schema.

Sequel Pro wrote the dump in ``db_dumps/glyph_latest.sql``. It has one
multi-row INSERT statement for each table. The text columns used a binary
collation, so the dump gives their values as hexadecimal literals of UTF-8
bytes.
"""

import re
from collections.abc import Iterator
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from sqlalchemy import Column, Connection, DateTime, MetaData

type Value = int | float | str | None

# Tables in the dump that are not part of the application schema.
IGNORED_TABLES = frozenset({"alembic_version"})

INSERT_RE = re.compile(
    r"INSERT INTO `(?P<table>\w+)` \((?P<columns>[^)]*)\)\s*VALUES", re.IGNORECASE
)
TOKEN_RE = re.compile(
    r"""\s*(?:
        (?P<null>NULL)
      | (?P<number>-?\d+(?:\.\d+)?)
      | [Xx]'(?P<hex>[0-9A-Fa-f]*)'
      | '(?P<string>(?:[^'\\]|\\.|'')*)'
      | (?P<punct>[(),;])
    )""",
    re.VERBOSE | re.DOTALL,
)
ESCAPE_RE = re.compile(r"\\(.)|''", re.DOTALL)
MYSQL_ESCAPES = {"0": "\0", "b": "\b", "n": "\n", "r": "\r", "t": "\t", "Z": "\x1a"}


class DumpError(ValueError):
    """The dump cannot be parsed, or it does not fit the schema."""


@dataclass(frozen=True)
class Insert:
    table: str
    columns: tuple[str, ...]
    rows: list[tuple[Value, ...]]


def parse_inserts(sql: str) -> Iterator[Insert]:
    """Yield the INSERT statements in a MySQL dump, in file order."""
    pos = 0
    while (match := INSERT_RE.search(sql, pos)) is not None:
        columns = tuple(name.strip().strip("`") for name in match["columns"].split(","))
        scanner = _Scanner(sql, match.end())
        yield Insert(match["table"], columns, scanner.rows(len(columns)))
        pos = scanner.pos


def load_dump(connection: Connection, metadata: MetaData, sql: str) -> dict[str, int]:
    """Replace the rows of every table in ``metadata`` with the rows in ``sql``.

    Return the number of rows loaded into each table. The caller owns the
    transaction, and must roll it back if this function raises.
    """
    inserts = [i for i in parse_inserts(sql) if i.table not in IGNORED_TABLES]
    for insert in inserts:
        table = metadata.tables.get(insert.table)
        if table is None:
            raise DumpError(f"unknown table {insert.table!r}")
        unknown = set(insert.columns).difference(table.c.keys())
        if unknown:
            names = ", ".join(sorted(unknown))
            raise DumpError(f"unknown columns in {insert.table!r}: {names}")

    for table in reversed(metadata.sorted_tables):
        connection.execute(table.delete())
    # The dump does not order tables by dependency. SQLite resets this pragma
    # when the transaction ends.
    connection.exec_driver_sql("PRAGMA defer_foreign_keys = ON")

    counts: dict[str, int] = {}
    for insert in inserts:
        table = metadata.tables[insert.table]
        columns = [table.c[name] for name in insert.columns]
        records = [
            {
                column.key: _convert(column, value)
                for column, value in zip(columns, row, strict=True)
            }
            for row in insert.rows
        ]
        if records:
            connection.execute(table.insert(), records)
        counts[insert.table] = counts.get(insert.table, 0) + len(records)

    violations = connection.exec_driver_sql("PRAGMA foreign_key_check").fetchall()
    if violations:
        child, rowid, parent, _ = violations[0]
        raise DumpError(
            f"{len(violations)} rows break foreign key constraints; the first is "
            f"row {rowid} of {child!r}, which refers to a missing {parent!r} row"
        )
    return counts


def _convert(column: Column[Any], value: Value) -> object:
    if isinstance(value, str) and isinstance(column.type, DateTime):
        return datetime.fromisoformat(value)
    return value


def _unescape(body: str) -> str:
    def replace(match: re.Match[str]) -> str:
        char = match[1]
        if char is None:
            return "'"
        if char in "%_":
            return "\\" + char
        return MYSQL_ESCAPES.get(char, char)

    return ESCAPE_RE.sub(replace, body)


class _Scanner:
    """Read the value tuples of one INSERT statement."""

    def __init__(self, sql: str, pos: int) -> None:
        self.sql = sql
        self.pos = pos

    def rows(self, width: int) -> list[tuple[Value, ...]]:
        rows: list[tuple[Value, ...]] = []
        while True:
            self._punctuation("(")
            row = [self._value()]
            while self._punctuation(",)") == ",":
                row.append(self._value())
            if len(row) != width:
                raise self._error(f"expected {width} values, found {len(row)}")
            rows.append(tuple(row))
            if self._punctuation(",;") == ";":
                return rows

    def _punctuation(self, allowed: str) -> str:
        match = self._next()
        punct = match["punct"]
        if punct is None or punct not in allowed:
            raise self._error(f"expected one of {' '.join(allowed)}")
        return punct

    def _value(self) -> Value:
        match = self._next()
        if match["null"] is not None:
            return None
        if (number := match["number"]) is not None:
            return float(number) if "." in number else int(number)
        if (digits := match["hex"]) is not None:
            try:
                return bytes.fromhex(digits).decode("utf-8")
            except UnicodeDecodeError as error:
                raise self._error("hexadecimal literal is not UTF-8") from error
        if (body := match["string"]) is not None:
            return _unescape(body)
        raise self._error("expected a value")

    def _next(self) -> re.Match[str]:
        match = TOKEN_RE.match(self.sql, self.pos)
        if match is None:
            raise self._error("unexpected input")
        self.pos = match.end()
        return match

    def _error(self, message: str) -> DumpError:
        line = self.sql.count("\n", 0, self.pos) + 1
        return DumpError(f"{message} at line {line}")
