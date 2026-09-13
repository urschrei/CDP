"""Snapshots of catalogue entries for the tablets, for links from tablet pages.

The CDP writes the spaces and the punctuation of a museum number as
underscores, as in BM_91082 and 81_2-4_287. The catalogues write the same
numbers in other forms, as in BM 091082 and 1881-02-04, 0287. A key made of the
letters and the numbers of a museum number, without zeros in front of the
numbers, is the same for these forms.

CDLI lets users copy and re-use the text of its catalogue, with a reference to
CDLI: https://cdli.earth/terms-of-use
"""

import csv
import io
import re
import urllib.request
from collections import defaultdict
from collections.abc import Iterable, Iterator, Mapping
from contextlib import contextmanager
from pathlib import Path

import click
from flask.cli import with_appcontext
from sqlalchemy import delete, select

from cdpp.db import db
from cdpp.models import CdliArtifact, Tablet

CDLI_CATALOGUE_URL = (
    "https://media.githubusercontent.com/media/cdli-gh/data/master/cdli_cat.csv"
)
CDLI_PAGE_URL = "https://cdli.earth/{p_number}"
# The fields of a CDLI catalogue row that the snapshot keeps.
CDLI_FIELDS = (
    "id_text",
    "designation",
    "museum_no",
    "accession_no",
    "primary_publication",
    "publication_history",
)
# CDLI writes these collection names in front of some museum numbers. The CDP
# does not.
COLLECTION_PREFIXES = frozenset({"ASHM", "OIM", "UM"})
# Fields of the CDLI catalogue can be longer than the default limit of csv.
FIELD_SIZE_LIMIT = 2**31 - 1

type CatalogueRow = Mapping[str, str]


def museum_number_key(text: str) -> str | None:
    """Return the key of one museum number, or None if it has no number."""
    tokens = re.findall(r"[A-Za-z]+|\d+", text)
    if not any(token.isdigit() for token in tokens):
        return None
    parts = [str(int(token)) if token.isdigit() else token.upper() for token in tokens]
    # A registration number of the British Museum with a year of two digits, as
    # in 81-2-4, 287, is in the 19th century.
    if (
        len(tokens) == 4
        and all(token.isdigit() for token in tokens)
        and len(tokens[0]) == 2
    ):
        parts[0] = f"18{parts[0]}"
    return ".".join(parts)


def tablet_key(museum_number: str) -> str | None:
    """Return the key of a CDP museum number.

    A seal impression, as in BM_14030_seal, has the number of its tablet.
    """
    return museum_number_key(re.sub(r"_seal$", "", museum_number))


def catalogue_keys(text: str | None) -> set[str]:
    """Return the keys of the museum numbers in a catalogue field.

    A field can name joined fragments, as in K 00039 + K 00153, and a former
    number, as in BM 091082 (was BM 012225). A registration number can contain
    letters, as in 1891-05-09 Bu, 0003.
    """
    keys: set[str] = set()
    if not text:
        return keys
    text = re.sub(r"\(was [^)]*\)", "", text)
    for part in re.split(r"[+&;()=]", text):
        key = museum_number_key(part)
        if key is None:
            continue
        keys.add(key)
        prefix, _, rest = key.partition(".")
        if prefix in COLLECTION_PREFIXES and rest:
            keys.add(rest)
        if re.match(r"\d{4}\.", key):
            keys.add(".".join(p for p in key.split(".") if p.isdigit()))
    return keys


def match_cdli(
    rows: Iterable[CatalogueRow], tablets: Mapping[int, str]
) -> dict[int, list[CatalogueRow]]:
    """Return the CDLI rows of each tablet.

    ``tablets`` maps tablet IDs to museum numbers. A row matches a tablet if
    its museum number or its accession number has the key of the tablet. The
    ranks of a match, from best to worst, are:

    0. The museum number names the object alone.
    1. The museum number names a join.
    2. The accession number has the key, and the museum number names no
       object, as in "BM —".
    3. The accession number has the key, and the museum number names a
       different object, as in "BM 134596 +" for K 15272.

    Only the rows of the best rank of each tablet are returned.
    """
    by_key: dict[str, list[int]] = defaultdict(list)
    for tablet_id, museum_number in tablets.items():
        if key := tablet_key(museum_number):
            by_key[key].append(tablet_id)

    found: dict[int, dict[int, list[CatalogueRow]]] = defaultdict(
        lambda: defaultdict(list)
    )
    for row in rows:
        museum_no = row.get("museum_no", "")
        museum_keys = catalogue_keys(museum_no)
        accession_keys = catalogue_keys(row.get("accession_no")) - museum_keys
        candidates = [
            (1 if re.search(r"[+&]", museum_no) else 0, museum_keys),
            (3 if museum_keys else 2, accession_keys),
        ]
        kept = {field: row.get(field, "") for field in CDLI_FIELDS}
        for rank, keys in candidates:
            for key in keys & by_key.keys():
                for tablet_id in by_key[key]:
                    if kept not in found[tablet_id][rank]:
                        found[tablet_id][rank].append(kept)
    return {tablet_id: ranks[min(ranks)] for tablet_id, ranks in found.items()}


def p_number(id_text: str) -> str:
    return f"P{int(id_text):06d}"


def replace_cdli_snapshot(rows: Iterable[CatalogueRow]) -> tuple[int, int]:
    """Replace the CDLI snapshot with the rows that match tablets.

    Return the number of matched tablets and the number of catalogue entries.
    """
    query = select(Tablet.id, Tablet.museum_number)
    tablets = {tablet_id: number for tablet_id, number in db.session.execute(query)}
    matches = match_cdli(rows, tablets)
    db.session.execute(delete(CdliArtifact))
    entries = 0
    for tablet_id, matched in sorted(matches.items()):
        for row in matched:
            db.session.add(
                CdliArtifact(
                    tablet_id=tablet_id,
                    p_number=p_number(row["id_text"]),
                    designation=row["designation"],
                    museum_no=row["museum_no"] or None,
                    accession_no=row["accession_no"] or None,
                    primary_publication=row["primary_publication"] or None,
                    publication_history=row["publication_history"] or None,
                )
            )
            entries += 1
    db.session.commit()
    return len(matches), entries


def catalogue_links(tablet_id: int) -> list[tuple[str, list[tuple[str, str]]]]:
    """Return the links of a tablet page to catalogue entries, by catalogue."""
    artifacts = db.session.scalars(
        select(CdliArtifact)
        .where(CdliArtifact.tablet_id == tablet_id)
        .order_by(CdliArtifact.p_number)
    ).all()
    links: list[tuple[str, list[tuple[str, str]]]] = []
    if artifacts:
        cdli = [
            (artifact.p_number, CDLI_PAGE_URL.format(p_number=artifact.p_number))
            for artifact in artifacts
        ]
        links.append(("CDLI", cdli))
    return links


@contextmanager
def open_text(source: str) -> Iterator[io.TextIOBase]:
    """Open a UTF-8 text file from a path or from an HTTP or HTTPS URL."""
    if source.startswith(("https://", "http://")):
        with urllib.request.urlopen(source, timeout=600) as response:
            yield io.TextIOWrapper(response, encoding="utf-8", newline="")
    else:
        with Path(source).open(encoding="utf-8", newline="") as file:
            yield file


@click.command("import-cdli")
@click.argument("source", default=CDLI_CATALOGUE_URL)
@with_appcontext
def import_cdli(source: str) -> None:
    """Replace the snapshot of the CDLI catalogue entries of the tablets.

    SOURCE is a path or a URL of the CDLI catalogue in CSV, and defaults to the
    file in the CDLI data repository. Run 'cdpp dump-data' afterwards.
    """
    csv.field_size_limit(FIELD_SIZE_LIMIT)
    with open_text(source) as lines:
        tablets, entries = replace_cdli_snapshot(csv.DictReader(lines))
    click.echo(f"Matched {tablets} tablets to {entries} CDLI catalogue entries.")
