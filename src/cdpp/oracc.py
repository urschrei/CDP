"""A snapshot of the Oracc Sign List (OSL), for links to its sign pages.

The tables oracc_sign and oracc_list_number hold the snapshot, and
``cdpp import-oracc-signs`` replaces it. The OSL source file, osl.asl, is in the
public domain under a CC0 licence: https://github.com/oracc/osl
"""

import re
import urllib.request
from collections import defaultdict
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import quote

from sqlalchemy import delete, select, tuple_

from cdpp.db import db
from cdpp.models import OraccListNumber, OraccSign, SignListEntry

OSL_URL = "https://raw.githubusercontent.com/oracc/osl/master/00lib/osl.asl"
# The citation URL that OSL gives on each sign page.
PAGE_URL = "http://oracc.org/osl/signlist/{oid}"

HEADING_RE = re.compile(r"@(sign|form)(-?)\s+(\S+)")
LIST_NUMBER_RE = re.compile(r"([A-Z]+)(\d.*)")
NUMBER_RE = re.compile(r"(\d+)(.*)")


@dataclass
class OslEntry:
    """A sign or a sign form in osl.asl."""

    name: str
    oid: str | None = None
    ebl_url: str | None = None
    numbers: list[tuple[str, str]] = field(default_factory=list)


def parse_osl(lines: Iterable[str]) -> list[OslEntry]:
    """Return the signs and forms in osl.asl that have an ID.

    A sign ends at "@end sign". A form starts inside a sign and ends at "@@".
    The parser skips the signs and forms that OSL marks as removed, with
    "@sign-" or "@form-", and the forms of a removed sign.
    """
    entries: list[OslEntry] = []
    sign: OslEntry | None = None
    current: OslEntry | None = None
    for line in lines:
        if heading := HEADING_RE.match(line):
            kind, removed, name = heading.groups()
            if kind == "sign":
                sign = current = None if removed else OslEntry(name)
            else:
                current = None if removed or sign is None else OslEntry(name)
            if current is not None:
                entries.append(current)
        elif line.startswith("@@"):
            current = sign
        elif line.startswith("@end sign"):
            sign = current = None
        elif current is not None:
            fields = line.split(maxsplit=1)
            if len(fields) < 2:
                continue
            directive, value = fields[0], fields[1].strip()
            if directive == "@oid":
                current.oid = value
            elif directive == "@list" and (number := LIST_NUMBER_RE.fullmatch(value)):
                current.numbers.append((number[1], number[2]))
            elif directive == "@link" and value.startswith("eBL "):
                current.ebl_url = quote(value.rsplit(maxsplit=1)[-1], safe=":/")
    return [entry for entry in entries if entry.oid]


def read_osl(source: str) -> list[OslEntry]:
    """Parse osl.asl from a path or from an HTTP or HTTPS URL."""
    if source.startswith(("https://", "http://")):
        with urllib.request.urlopen(source, timeout=60) as response:
            text = response.read().decode("utf-8")
    else:
        text = Path(source).read_text(encoding="utf-8")
    return parse_osl(text.splitlines())


def replace_snapshot(entries: Iterable[OslEntry]) -> tuple[int, int]:
    """Replace the OSL snapshot with ``entries``.

    Return the number of signs and forms, and the number of list numbers.
    """
    db.session.execute(delete(OraccListNumber))
    db.session.execute(delete(OraccSign))
    oids: set[str] = set()
    numbers = 0
    for entry in entries:
        if entry.oid is None or entry.oid in oids:
            continue
        oids.add(entry.oid)
        list_numbers = [
            OraccListNumber(list_name=list_name, number=number)
            for list_name, number in dict.fromkeys(entry.numbers)
        ]
        numbers += len(list_numbers)
        db.session.add(
            OraccSign(
                oid=entry.oid,
                name=entry.name,
                ebl_url=entry.ebl_url,
                list_numbers=list_numbers,
            )
        )
    db.session.commit()
    return len(oids), numbers


def number_forms(number: str) -> tuple[str, ...]:
    """Return the forms of a sign-list number to look up in the OSL snapshot.

    OSL writes numbers with at least three digits, as in MZL001, and keeps any
    suffix, as in ABZL219a.
    """
    match = NUMBER_RE.fullmatch(number)
    if match is None:
        return (number,)
    padded = f"{int(match[1]):03d}{match[2]}"
    return (padded,) if padded == number else (padded, number)


def oracc_page_url(oid: str) -> str:
    return PAGE_URL.format(oid=oid)


def list_number_signs(entries: Sequence[SignListEntry]) -> dict[int, OraccSign]:
    """Map the IDs of sign-list entries to OSL signs and forms.

    An entry has an OSL sign or form if its sign list has an OSL abbreviation,
    and exactly one OSL sign or form has the number of the entry in that list.
    The sign lists of the entries must be loaded.
    """
    pairs = {
        (entry.sign_list.oracc_list, form)
        for entry in entries
        if entry.sign_list.oracc_list is not None
        for form in number_forms(entry.number)
    }
    if not pairs:
        return {}
    statement = (
        select(OraccListNumber.list_name, OraccListNumber.number, OraccSign)
        .join(OraccListNumber.oracc_sign)
        .where(
            tuple_(OraccListNumber.list_name, OraccListNumber.number).in_(sorted(pairs))
        )
    )
    matches: dict[tuple[str, str], dict[str, OraccSign]] = defaultdict(dict)
    for list_name, number, oracc_sign in db.session.execute(statement):
        matches[(list_name, number)][oracc_sign.oid] = oracc_sign

    signs: dict[int, OraccSign] = {}
    for entry in entries:
        oracc_list = entry.sign_list.oracc_list
        found = next(
            (
                matches[(oracc_list, form)]
                for form in number_forms(entry.number)
                if oracc_list is not None and (oracc_list, form) in matches
            ),
            {},
        )
        if len(found) == 1:
            signs[entry.id] = next(iter(found.values()))
    return signs


def signs_named(names: Iterable[str]) -> dict[str, OraccSign]:
    """Map each name to the OSL sign or form with that name, if exactly one has it."""
    wanted = set(names)
    if not wanted:
        return {}
    found: dict[str, list[OraccSign]] = defaultdict(list)
    statement = select(OraccSign).where(OraccSign.name.in_(wanted))
    for oracc_sign in db.session.scalars(statement):
        found[oracc_sign.name].append(oracc_sign)
    return {name: signs[0] for name, signs in found.items() if len(signs) == 1}
