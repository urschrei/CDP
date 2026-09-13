"""Full-text search of signs and tablets, with SQLite FTS5.

The search tables are derived from the other tables. They are not in the
models, the migrations or the data dump. ``rebuild`` makes them from the
database, and a search makes them if they do not exist.
"""

import sqlite3
import unicodedata
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

from sqlalchemy import select, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import selectinload

from cdpp.db import db
from cdpp.models import Cdp, Sign, Tablet

SIGN_TABLE = "search_sign"
TABLET_TABLE = "search_tablet"
SEARCH_TABLES = (SIGN_TABLE, TABLET_TABLE)
# The fields of each document, in order of ranking weight.
SIGN_FIELDS = ("sign_ref", "names")
TABLET_FIELDS = (
    "museum_number",
    "rulers",
    "city",
    "locality",
    "period",
    "sub_period",
    "genre",
    "text_vehicle",
    "medium",
    "method",
    "publication",
    "notes",
)
# The trigram tokenizer cannot find a text shorter than three characters. A
# shorter query reads all the documents instead.
TRIGRAM_LENGTH = 3
# Separates the values of a field that has more than one value.
SEPARATOR = "\n"


@dataclass(frozen=True)
class SearchResults:
    """Record IDs in rank order, with the number of all matches."""

    sign_ids: list[int]
    tablet_ids: list[int]
    sign_count: int
    tablet_count: int


def normalise(value: str) -> str:
    """Return ``value`` in the form that a search compares.

    NFKC changes subscript digits to digits, so "gir3" finds GIR₃. It keeps
    Š and S different.
    """
    return unicodedata.normalize("NFKC", value).casefold()


def search_records(query: str, limit: int) -> SearchResults:
    """Find the signs and tablets that contain ``query`` in one of their fields."""
    needle = normalise(query.strip())
    try:
        sign_ids = matching_ids(SIGN_TABLE, SIGN_FIELDS, needle)
    except OperationalError as error:
        if "no such table" not in str(error.orig):
            raise
        db.session.rollback()
        rebuild()
        sign_ids = matching_ids(SIGN_TABLE, SIGN_FIELDS, needle)
    tablet_ids = matching_ids(TABLET_TABLE, TABLET_FIELDS, needle)
    return SearchResults(
        sign_ids=sign_ids[:limit],
        tablet_ids=tablet_ids[:limit],
        sign_count=len(sign_ids),
        tablet_count=len(tablet_ids),
    )


def matching_ids(table: str, fields: Sequence[str], needle: str) -> list[int]:
    """Return the IDs of the documents that contain ``needle``, best match first."""
    if not needle:
        return []
    columns = ", ".join(fields)
    if len(needle) >= TRIGRAM_LENGTH:
        phrase = '"' + needle.replace('"', '""') + '"'
        rows = db.session.execute(
            text(f"SELECT rowid, {columns} FROM {table} WHERE {table} MATCH :phrase"),
            {"phrase": phrase},
        )
    else:
        rows = db.session.execute(text(f"SELECT rowid, {columns} FROM {table}"))
    ranked = [
        (key, rowid)
        for rowid, *values in rows
        if (key := rank(needle, values)) is not None
    ]
    return [rowid for _, rowid in sorted(ranked)]


def rank(needle: str, fields: Sequence[str]) -> tuple[int, int, int] | None:
    """Return the sort key of a document for ``needle``, or None if it does not match.

    An exact value ranks first, then a value that starts with ``needle``, then
    a value that contains it. Then an earlier field ranks first, and then a
    shorter value.
    """
    keys = []
    for position, field in enumerate(fields):
        for value in field.split(SEPARATOR):
            if value == needle:
                tier = 0
            elif value.startswith(needle):
                tier = 1
            elif needle in value:
                tier = 2
            else:
                continue
            keys.append((tier, position, len(value)))
    return min(keys, default=None)


def rebuild() -> tuple[int, int]:
    """Make the search tables again. Return the numbers of signs and tablets."""
    signs = sign_documents()
    tablets = tablet_documents()
    fill(SIGN_TABLE, SIGN_FIELDS, signs)
    fill(TABLET_TABLE, TABLET_FIELDS, tablets)
    db.session.commit()
    return len(signs), len(tablets)


def fill(table: str, fields: Sequence[str], documents: list[dict[str, Any]]) -> None:
    columns = ", ".join(fields)
    db.session.execute(text(f"DROP TABLE IF EXISTS {table}"))
    db.session.execute(
        text(f"CREATE VIRTUAL TABLE {table} USING fts5({columns}, tokenize='trigram')")
    )
    if documents:
        placeholders = ", ".join(f":{field}" for field in fields)
        db.session.execute(
            text(
                f"INSERT INTO {table} (rowid, {columns}) VALUES (:id, {placeholders})"
            ),
            [
                {"id": document["id"]}
                | {field: field_text(document[field]) for field in fields}
                for document in documents
            ],
        )


def field_text(value: str | list[str] | None) -> str:
    if value is None:
        return ""
    if isinstance(value, list):
        return SEPARATOR.join(normalise(item) for item in value)
    return normalise(value)


def drop_tables(connection: sqlite3.Connection) -> None:
    """Remove the search tables, for example from a copy of the database for a dump."""
    for table in SEARCH_TABLES:
        connection.execute(f"DROP TABLE IF EXISTS {table}")


def sign_documents() -> list[dict[str, Any]]:
    statement = (
        select(Sign)
        .order_by(Sign.id)
        .options(selectinload(Sign.cdp_records).selectinload(Cdp.names))
    )
    return [sign_document(sign) for sign in db.session.scalars(statement)]


def sign_document(sign: Sign) -> dict[str, Any]:
    """Describe a sign by its CDP name and its names in other sign lists."""
    names = {name.name for record in sign.cdp_records for name in record.names}
    names.discard(sign.sign_ref)
    return {"id": sign.id, "sign_ref": sign.sign_ref, "names": sorted(names)}


def tablet_documents() -> list[dict[str, Any]]:
    statement = select(Tablet).order_by(Tablet.id).options(selectinload(Tablet.rulers))
    return [tablet_document(tablet) for tablet in db.session.scalars(statement)]


def tablet_document(tablet: Tablet) -> dict[str, Any]:
    return {
        "id": tablet.id,
        "museum_number": tablet.museum_number,
        "rulers": [ruler.name for ruler in tablet.rulers],
        "city": tablet.city.name if tablet.city else None,
        "locality": tablet.locality.area if tablet.locality else None,
        "period": tablet.period.name,
        "sub_period": tablet.sub_period.name if tablet.sub_period else None,
        "genre": tablet.genre.name if tablet.genre else None,
        "text_vehicle": tablet.text_vehicle.name if tablet.text_vehicle else None,
        "medium": tablet.medium.name,
        "method": tablet.method.name if tablet.method else None,
        "publication": tablet.publication,
        "notes": tablet.notes,
    }
