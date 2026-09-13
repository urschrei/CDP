"""Full-text search of signs and tablets, with SQLite FTS5.

The search tables are derived from the other tables. They are not in the
models, the migrations or the data dump. ``rebuild`` makes them from the
database. A search makes them if they do not exist, or if their fields are not
the fields of this version.
"""

import sqlite3
import unicodedata
from collections import defaultdict
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from sqlalchemy import select, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import joinedload, selectinload

from cdpp.cdli_comparison import CITY_NAMES, cdli_periods, cdli_place, city_agrees
from cdpp.dates import year_text
from cdpp.db import db
from cdpp.models import (
    CdliArtifact,
    Cdp,
    City,
    Correspondent,
    Eponym,
    EponymYear,
    Instance,
    Language,
    OraccText,
    Sign,
    Tablet,
)

SIGN_TABLE = "search_sign"
TABLET_TABLE = "search_tablet"
SEARCH_TABLES = (SIGN_TABLE, TABLET_TABLE)
# The fields of each document, in order of ranking weight.
SIGN_FIELDS = ("sign_ref", "names")
TABLET_FIELDS = (
    "museum_number",
    "identifiers",
    "rulers",
    "eponym",
    "year",
    "city",
    "city_names",
    "origin_city",
    "locality",
    "period",
    "sub_period",
    "period_names",
    "correspondents",
    "languages",
    "genre",
    "text_vehicle",
    "script_type",
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
# SQLite errors of search tables that do not exist, or that have other fields.
OUTDATED_TABLE_ERRORS = ("no such table", "no such column")


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
        sign_ids, tablet_ids = matches(needle)
    except OperationalError as error:
        if not any(message in str(error.orig) for message in OUTDATED_TABLE_ERRORS):
            raise
        db.session.rollback()
        rebuild()
        sign_ids, tablet_ids = matches(needle)
    return SearchResults(
        sign_ids=sign_ids[:limit],
        tablet_ids=tablet_ids[:limit],
        sign_count=len(sign_ids),
        tablet_count=len(tablet_ids),
    )


def matches(needle: str) -> tuple[list[int], list[int]]:
    return (
        matching_ids(SIGN_TABLE, SIGN_FIELDS, needle),
        matching_ids(TABLET_TABLE, TABLET_FIELDS, needle),
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


@dataclass(frozen=True)
class TabletValues:
    """Values from other tables for the documents of tablets.

    ``identifiers`` and ``languages`` are by tablet ID, ``city_names`` by city
    ID, and ``eponyms`` by year.
    """

    identifiers: Mapping[int, list[str]]
    languages: Mapping[int, list[str]]
    city_names: Mapping[int, list[str]]
    eponyms: Mapping[int, str]

    @classmethod
    def load(cls) -> TabletValues:
        return cls(
            catalogue_identifiers(),
            instance_languages(),
            other_city_names(),
            {
                year: eponym
                for year, eponym in db.session.execute(
                    select(EponymYear.year, Eponym.name).join(
                        Eponym, Eponym.id == EponymYear.eponym_id
                    )
                )
            },
        )


def catalogue_identifiers() -> dict[int, list[str]]:
    """Return the CDLI and Oracc identifiers of each tablet.

    They are the P-numbers, the museum and accession numbers as CDLI writes
    them, as in BM 091082, and the IDs of the Oracc texts.
    """
    found: dict[int, list[str]] = defaultdict(list)
    artifacts = select(
        CdliArtifact.tablet_id,
        CdliArtifact.p_number,
        CdliArtifact.museum_no,
        CdliArtifact.accession_no,
    ).order_by(CdliArtifact.p_number)
    for tablet_id, *values in db.session.execute(artifacts):
        found[tablet_id] += [value for value in values if value]
    texts = select(OraccText.tablet_id, OraccText.text_id).order_by(OraccText.text_id)
    for tablet_id, text_id in db.session.execute(texts):
        found[tablet_id].append(text_id)
    return {
        tablet_id: list(dict.fromkeys(values)) for tablet_id, values in found.items()
    }


def instance_languages() -> dict[int, list[str]]:
    """Return the languages of the sign instances of each tablet."""
    found: dict[int, list[str]] = defaultdict(list)
    rows = db.session.execute(
        select(Instance.tablet_id, Language.name)
        .join(Language, Language.id == Instance.language_id)
        .distinct()
        .order_by(Instance.tablet_id, Language.name)
    )
    for tablet_id, language in rows:
        found[tablet_id].append(language)
    return found


def other_city_names() -> dict[int, list[str]]:
    """Return the other names of each city.

    They are the names in CITY_NAMES, and the ancient and modern names of the
    CDLI places that agree with the city, as in Kanesh and Kültepe for Kultepe.
    """
    cities = {
        city_id: name
        for city_id, name in db.session.execute(select(City.id, City.name))
    }
    found: dict[int, set[str]] = defaultdict(set)
    for city_id, city in cities.items():
        found[city_id].update(CITY_NAMES.get(city, ()))
    places = select(Tablet.city_id, CdliArtifact.provenience).join(
        CdliArtifact, CdliArtifact.tablet_id == Tablet.id
    )
    for city_id, provenience in db.session.execute(places):
        place = cdli_place(provenience)
        if city_id is not None and place and city_agrees(cities[city_id], provenience):
            found[city_id].update(place)
    return {
        city_id: sorted(names - {cities[city_id]})
        for city_id, names in found.items()
        if names - {cities[city_id]}
    }


def tablet_documents() -> list[dict[str, Any]]:
    statement = (
        select(Tablet)
        .order_by(Tablet.id)
        .options(
            selectinload(Tablet.rulers),
            selectinload(Tablet.recipients).options(
                joinedload(Correspondent.ruler),
                joinedload(Correspondent.non_ruler),
            ),
        )
    )
    values = TabletValues.load()
    return [tablet_document(tablet, values) for tablet in db.session.scalars(statement)]


def tablet_document(tablet: Tablet, values: TabletValues) -> dict[str, Any]:
    period = tablet.period.name
    sub_period = tablet.sub_period.name if tablet.sub_period else None
    # Museum numbers use underscores for spaces, as in BM_91082.
    spaced = tablet.museum_number.replace("_", " ")
    identifiers = [spaced] if spaced != tablet.museum_number else []
    correspondents = [tablet.sent_from, *tablet.recipients]
    return {
        "id": tablet.id,
        "museum_number": tablet.museum_number,
        "identifiers": identifiers + values.identifiers.get(tablet.id, []),
        "rulers": [ruler.name for ruler in tablet.rulers],
        "eponym": tablet.eponym.name
        if tablet.eponym
        else values.eponyms.get(tablet.year)
        if tablet.year is not None
        else None,
        "year": None if tablet.year is None else year_text(tablet.year),
        "city": tablet.city.name if tablet.city else None,
        "city_names": values.city_names.get(tablet.city_id, [])
        if tablet.city_id is not None
        else [],
        "origin_city": tablet.origin_city.name if tablet.origin_city else None,
        "locality": tablet.locality.area if tablet.locality else None,
        "period": period,
        "sub_period": sub_period,
        "period_names": [
            name
            for name in cdli_periods(period, sub_period)
            if name not in (period, sub_period)
        ],
        "correspondents": [
            name for party in correspondents if party and (name := party.name)
        ],
        "languages": values.languages.get(tablet.id, []),
        "genre": tablet.genre.name if tablet.genre else None,
        "text_vehicle": tablet.text_vehicle.name if tablet.text_vehicle else None,
        "script_type": tablet.script_type.script if tablet.script_type else None,
        "medium": tablet.medium.name,
        "method": tablet.method.name if tablet.method else None,
        "publication": tablet.publication,
        "notes": tablet.notes,
    }
