"""Comparison of the tablets with their entries in the snapshot of the CDLI catalogue.

``cdpp check-cdli`` writes the tables of the questions for the editors about the
tablets whose period, city, object or language does not agree with their CDLI
entries. The data and CDLI give different names to some periods, places and
object types. The tables of names below state which names agree. The questions
show these tables, so that the editors can approve them.
"""

import re
import unicodedata
from collections import defaultdict
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

import click
from flask.cli import with_appcontext
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from cdpp.db import db
from cdpp.models import CdliArtifact, Instance, Tablet

QUESTIONS_PATH = "docs/questions-for-the-editors.md"
SECTION_START = "<!-- cdpp check-cdli: {name} -->"
SECTION_END = "<!-- cdpp check-cdli: end -->"

# CDLI values that give no period, place, object type or language.
UNKNOWN = frozenset(
    {
        "no linguistic content",
        "other",
        "other (see object remarks)",
        "uncertain",
        "unclear",
        "undetermined",
        "uninscribed",
    }
)


@dataclass(frozen=True)
class PeriodTerm:
    """The period in the data that a CDLI period agrees with.

    If ``sub_periods`` is empty, all sub-periods agree. If not, the tablet must
    have one of these sub-periods, or no sub-period.
    """

    period: str
    sub_periods: frozenset[str] = frozenset()


def period_term(period: str, *sub_periods: str) -> PeriodTerm:
    return PeriodTerm(period, frozenset(sub_periods))


# CDLI periods without their dates, and the periods in the data that agree.
PERIODS = {
    "Uruk IV": period_term("Archaic"),
    "Uruk III": period_term("Archaic"),
    "ED I-II": period_term("Early Dynastic", "ED I"),
    "ED IIIa": period_term("Early Dynastic", "ED IIIa"),
    "ED IIIb": period_term("Early Dynastic", "ED IIIb"),
    "Old Akkadian": period_term("Late Third Millennium", "Old Akkadian"),
    "Lagash II": period_term("Late Third Millennium", "Lagash II"),
    "Ur III": period_term("Late Third Millennium", "Ur III"),
    "Early Old Babylonian": period_term("Old Babylonian", "Early Old Babylonian"),
    "Old Babylonian": period_term("Old Babylonian", "Late Old Babylonian"),
    "Old Assyrian": period_term("Old Assyrian"),
    "Middle Babylonian": period_term("Middle Babylonian"),
    "Middle Assyrian": period_term("Middle Assyrian"),
    "Neo-Assyrian": period_term("Neo-Assyrian"),
    "Early Neo-Babylonian": period_term("Neo-Babylonian", "Early Neo-Babylonian"),
    "Neo-Babylonian": period_term("Neo-Babylonian", "Chaldean"),
    "Achaemenid": period_term("Late Babylonian", "Achaemenid"),
    "Hellenistic": period_term("Late Babylonian", "Greek"),
}

# Cities in the data, and other names of them in CDLI. A city also agrees with
# a CDLI place of the same ancient or modern name.
CITY_NAMES = {
    "Ashur": frozenset({"Assur"}),
    "Drehem": frozenset({"Puzriš-Dagan"}),
    "Eshnunna": frozenset({"Ešnunna"}),
    "Kultepe": frozenset({"Kanesh"}),
    "Sippar": frozenset({"Sippar-Amnanum", "Sippar-Yahrurum"}),
}

# Object types in the data, and the CDLI object types that agree. Other object
# types agree with the CDLI object type of the same name.
OBJECT_TYPES = {
    "cylinder seal": frozenset({"seal (not impression)"}),
    "envelope": frozenset({"envelope", "tablet & envelope"}),
    "tablet": frozenset({"tablet", "tablet & envelope"}),
}

PLACE = re.compile(r"(?P<ancient>.*?)\s*\(mod\. (?P<modern>[^)]*)\)")

type Match = tuple[Tablet, Sequence[CdliArtifact]]
type Row = tuple[str, ...]


def fold(text: str) -> str:
    """Return a text without case and diacritics, as in "kultepe" for "Kültepe"."""
    decomposed = unicodedata.normalize("NFKD", text)
    letters = "".join(char for char in decomposed if not unicodedata.combining(char))
    return letters.casefold().strip()


def known(text: str | None) -> str | None:
    """Return a CDLI value without its question mark, or None if it gives no value."""
    value = (text or "").strip().removesuffix("?").strip()
    if not value or fold(value) in UNKNOWN:
        return None
    return value


def period_agrees(period: str, sub_period: str | None, text: str | None) -> bool | None:
    """Return whether a period and a sub-period agree with a CDLI period.

    Return None if the CDLI value gives no period. A CDLI period that is not in
    PERIODS does not agree.
    """
    value = known(text)
    if value is None:
        return None
    # CDLI writes the dates after the name, as in "Ur III (ca. 2100-2000 BC)".
    term = PERIODS.get(re.sub(r"\s*\([^)]*\)$", "", value))
    if term is None:
        return False
    return period == term.period and (
        not term.sub_periods or sub_period is None or sub_period in term.sub_periods
    )


def cdli_periods(period: str, sub_period: str | None) -> list[str]:
    """Return the CDLI periods that name a period and a sub-period of the data.

    A CDLI period that requires a sub-period does not name a tablet without
    that sub-period: Early Old Babylonian does not name an Old Babylonian
    tablet without a sub-period.
    """
    return [
        label
        for label, term in PERIODS.items()
        if term.period == period
        and (not term.sub_periods or sub_period in term.sub_periods)
    ]


def cdli_place(text: str | None) -> tuple[str, ...] | None:
    """Return the ancient name of a CDLI place, and its modern name if CDLI gives one.

    "Kanesh (mod. Kültepe) ?" gives Kanesh and Kültepe. Return None if CDLI does
    not know the place, as in "uncertain (mod. Babylonia)".
    """
    value = known(text)
    if value is None:
        return None
    match = PLACE.fullmatch(value)
    if match is None:
        return (value,)
    if fold(match["ancient"]) in UNKNOWN:
        return None
    return (match["ancient"], match["modern"])


def cdli_place_names(text: str | None) -> frozenset[str] | None:
    """Return the names of a CDLI place, folded, or None if CDLI does not know it."""
    place = cdli_place(text)
    return None if place is None else frozenset(fold(name) for name in place)


def city_agrees(city: str, text: str | None) -> bool | None:
    """Return whether a city agrees with a CDLI place.

    Return None if CDLI does not know the place.
    """
    names = cdli_place_names(text)
    if names is None:
        return None
    ours = {fold(name) for name in (city, *CITY_NAMES.get(city, ()))}
    return not ours.isdisjoint(names)


def object_type_agrees(text_vehicle: str, text: str | None) -> bool | None:
    """Return whether an object type agrees with a CDLI object type.

    Return None if the CDLI value gives no object type.
    """
    value = known(text)
    if value is None:
        return None
    names = OBJECT_TYPES.get(text_vehicle, frozenset({text_vehicle}))
    return fold(value) in {fold(name) for name in names}


def material_agrees(medium: str, text: str | None) -> bool | None:
    """Return whether a medium is the first material of a CDLI entry.

    "stone: diorite" and "stone; soapstone" agree with stone. Return None if
    the CDLI value gives no material.
    """
    value = known(text)
    if value is None:
        return None
    return fold(re.split(r"[:;,(]", value)[0]) == fold(medium)


def cdli_languages(text: str | None) -> frozenset[str]:
    """Return the folded languages of a CDLI entry.

    CDLI separates languages with semicolons or commas, as in "Sumerian; Akkadian".
    """
    parts = [known(part) for part in re.split(r"[;,]", text or "")]
    return frozenset(fold(part) for part in parts if part)


def languages_agree(languages: Iterable[str], text: str | None) -> bool | None:
    """Return whether one of the languages is a language of a CDLI entry.

    Return None if there are no languages, or if CDLI gives no language.
    """
    ours = {fold(language) for language in languages}
    theirs = cdli_languages(text)
    if not ours or not theirs:
        return None
    return not ours.isdisjoint(theirs)


def disagrees(results: Iterable[bool | None]) -> bool:
    """Return True if at least one entry has a value to compare, and no entry agrees."""
    compared = [result for result in results if result is not None]
    return bool(compared) and not any(compared)


# Markdown


@dataclass(frozen=True)
class Section:
    """The Markdown of a section, and the number of tablets in its tables."""

    text: str
    tablets: int


def table(headings: Row, rows: Sequence[Row]) -> str:
    if not rows:
        return "No tablets."
    lines = [headings, ("---",) * len(headings), *rows]
    return "\n".join(
        "| " + " | ".join(cell.replace("|", "\\|") for cell in line) + " |"
        for line in lines
    )


def page(tablet: Tablet) -> str:
    return f"`/tablets/{tablet.id}`"


def tablet_count(*tables: Sequence[Row]) -> int:
    return len({row[0] for rows in tables for row in rows})


def period_section(matches: Sequence[Match]) -> Section:
    terms = [
        (
            label,
            term.period,
            ", ".join(sorted(term.sub_periods)) + ", or none"
            if term.sub_periods
            else "all",
        )
        for label, term in PERIODS.items()
    ]
    rows: list[Row] = []
    for tablet, entries in matches:
        sub_period = tablet.sub_period.name if tablet.sub_period else None
        results = [
            period_agrees(tablet.period.name, sub_period, entry.period)
            for entry in entries
        ]
        if disagrees(results):
            rows += [
                (
                    tablet.museum_number,
                    page(tablet),
                    tablet.period.name,
                    sub_period or "",
                    entry.p_number,
                    entry.period or "",
                )
                for entry in entries
            ]
    rows.sort(key=lambda row: (row[2], row[3]))
    parts = (
        "These CDLI periods agree with these periods in the data:",
        table(("CDLI period", "Period", "Sub-periods"), terms),
        "The period in the data does not agree with CDLI:",
        table(
            ("Tablet", "Page", "Period", "Sub-period", "CDLI entry", "CDLI period"),
            rows,
        ),
    )
    return Section("\n\n".join(parts), tablet_count(rows))


def city_section(matches: Sequence[Match]) -> Section:
    names = [(city, ", ".join(sorted(other))) for city, other in CITY_NAMES.items()]
    different: list[Row] = []
    missing: list[Row] = []
    for tablet, entries in matches:
        if tablet.city is None:
            if any(cdli_place_names(entry.provenience) for entry in entries):
                missing += [
                    (
                        tablet.museum_number,
                        page(tablet),
                        entry.p_number,
                        entry.provenience or "",
                    )
                    for entry in entries
                ]
        elif disagrees(
            [city_agrees(tablet.city.name, entry.provenience) for entry in entries]
        ):
            different += [
                (
                    tablet.museum_number,
                    page(tablet),
                    tablet.city.name,
                    entry.p_number,
                    entry.provenience or "",
                )
                for entry in entries
            ]
    different.sort(key=lambda row: row[2])
    missing.sort(key=lambda row: row[3])
    parts = (
        "A city agrees with a CDLI place of the same ancient or modern name, with"
        " or without diacritics. These cities also agree with other names:",
        table(("City", "CDLI names"), names),
        "The city in the data does not agree with CDLI:",
        table(("Tablet", "Page", "City", "CDLI entry", "CDLI provenience"), different),
        "The data give no city, and CDLI gives a place:",
        table(("Tablet", "Page", "CDLI entry", "CDLI provenience"), missing),
    )
    return Section("\n\n".join(parts), tablet_count(different, missing))


def object_section(matches: Sequence[Match]) -> Section:
    types = [(name, ", ".join(sorted(other))) for name, other in OBJECT_TYPES.items()]
    rows: list[Row] = []
    for tablet, entries in matches:
        text_vehicle = tablet.text_vehicle.name if tablet.text_vehicle else None
        objects = (
            [object_type_agrees(text_vehicle, entry.object_type) for entry in entries]
            if text_vehicle
            else []
        )
        materials = [
            material_agrees(tablet.medium.name, entry.material) for entry in entries
        ]
        if disagrees(objects) or disagrees(materials):
            rows += [
                (
                    tablet.museum_number,
                    page(tablet),
                    text_vehicle or "",
                    tablet.medium.name,
                    entry.p_number,
                    entry.object_type or "",
                    entry.material or "",
                )
                for entry in entries
            ]
    rows.sort(key=lambda row: (row[2], row[3]))
    parts = (
        "An object type agrees with the CDLI object type of the same name. These"
        " object types also agree with other CDLI object types:",
        table(("Object type", "CDLI object types"), types),
        "A medium agrees with the first CDLI material: stone agrees with"
        " `stone: diorite`. The comparison does not use the CDLI object type"
        " `other (see object remarks)`.",
        "The object type or the medium in the data does not agree with CDLI:",
        table(
            (
                "Tablet",
                "Page",
                "Object type",
                "Medium",
                "CDLI entry",
                "CDLI object type",
                "CDLI material",
            ),
            rows,
        ),
    )
    return Section("\n\n".join(parts), tablet_count(rows))


def language_section(matches: Sequence[Match]) -> Section:
    different: list[Row] = []
    missing: list[Row] = []
    for tablet, entries in matches:
        languages = sorted(
            {
                instance.language.name
                for instance in tablet.instances
                if instance.language
            }
        )
        without = sum(1 for instance in tablet.instances if instance.language is None)
        if disagrees([languages_agree(languages, entry.language) for entry in entries]):
            different += [
                (
                    tablet.museum_number,
                    page(tablet),
                    ", ".join(languages),
                    entry.p_number,
                    entry.language or "",
                )
                for entry in entries
            ]
        if without and any(cdli_languages(entry.language) for entry in entries):
            missing += [
                (
                    tablet.museum_number,
                    page(tablet),
                    str(without),
                    str(len(tablet.instances)),
                    ", ".join(languages),
                    entry.p_number,
                    entry.language or "",
                )
                for entry in entries
            ]
    different.sort(key=lambda row: row[2])
    missing.sort(key=lambda row: -int(row[2]))
    parts = (
        "The languages of the signs in the data and the CDLI languages have no"
        " language in common:",
        table(
            ("Tablet", "Page", "Languages", "CDLI entry", "CDLI language"), different
        ),
        "Some signs have no language, and CDLI gives a language:",
        table(
            (
                "Tablet",
                "Page",
                "Without language",
                "All",
                "Languages of the other signs",
                "CDLI entry",
                "CDLI language",
            ),
            missing,
        ),
    )
    return Section("\n\n".join(parts), tablet_count(different, missing))


SECTIONS: Mapping[str, Callable[[Sequence[Match]], Section]] = {
    "period": period_section,
    "city": city_section,
    "object": object_section,
    "language": language_section,
}


def matched_tablets() -> list[Match]:
    """Return the tablets with CDLI entries, in the order of their museum numbers."""
    artifacts = db.session.scalars(
        select(CdliArtifact).order_by(CdliArtifact.p_number)
    ).all()
    by_tablet: dict[int, list[CdliArtifact]] = defaultdict(list)
    for artifact in artifacts:
        by_tablet[artifact.tablet_id].append(artifact)
    tablets = db.session.scalars(
        select(Tablet)
        .where(Tablet.id.in_(by_tablet))
        .order_by(Tablet.museum_number)
        .options(
            selectinload(Tablet.period),
            selectinload(Tablet.sub_period),
            selectinload(Tablet.city),
            selectinload(Tablet.text_vehicle),
            selectinload(Tablet.medium),
            selectinload(Tablet.instances).selectinload(Instance.language),
        )
    ).all()
    return [(tablet, by_tablet[tablet.id]) for tablet in tablets]


def replace_sections(text: str, sections: Mapping[str, str]) -> str:
    """Replace the text between the start and the end comment of each section.

    Raise ValueError if a section has no start comment or no end comment.
    """
    for name, content in sections.items():
        start = SECTION_START.format(name=name)
        begin = text.find(start)
        end = text.find(SECTION_END, begin) if begin >= 0 else -1
        if end < 0:
            raise ValueError(
                f"No section starts with {start} and ends with {SECTION_END}."
            )
        text = f"{text[:begin]}{start}\n\n{content}\n\n{text[end:]}"
    return text


@click.command("check-cdli")
@click.argument(
    "path",
    default=QUESTIONS_PATH,
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
)
@with_appcontext
def check_cdli(path: Path) -> None:
    """Write the tablets that do not agree with their CDLI entries.

    PATH is a Markdown file with the sections period, city, object and language.
    A section starts with a comment such as <!-- cdpp check-cdli: period -->, and
    ends with <!-- cdpp check-cdli: end -->. The command replaces the text
    between the comments. PATH defaults to docs/questions-for-the-editors.md.
    """
    matches = matched_tablets()
    sections = {name: make(matches) for name, make in SECTIONS.items()}
    contents = {name: section.text for name, section in sections.items()}
    try:
        text = replace_sections(path.read_text(encoding="utf-8"), contents)
    except ValueError as error:
        raise click.ClickException(f"{path}: {error}") from error
    path.write_text(text, encoding="utf-8")
    for name, section in sections.items():
        click.echo(f"{name}: {section.tablets} tablets")
