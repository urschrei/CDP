"""Filters for the tablet list.

Most filters select the tablets that have a related record with a given name.
The language filter selects the tablets with a sign instance in a given
language. The series filter selects the tablets whose publication is in a given
series. Tablet pages link to filtered lists, and the tablet list has a filter
form.
"""

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Any

from sqlalchemy import ColumnElement, Select, or_, select

from cdpp.db import db
from cdpp.models import (
    City,
    Correspondent,
    Eponym,
    Function,
    Genre,
    Instance,
    Language,
    Locality,
    Medium,
    Method,
    Period,
    Ruler,
    ScriptType,
    SubPeriod,
    Tablet,
    TextVehicle,
    Year,
)
from cdpp.publications import parse_publication


@dataclass(frozen=True)
class TabletFilter:
    key: str
    label: str
    condition: Callable[[str], ColumnElement[bool]]
    # The names that the filter form offers, as a query or as a function that
    # returns them. None if only links use the filter.
    options: Select[tuple[str]] | Callable[[], list[str]] | None = None


def _related(
    key: str, label: str, relationship: Any, name: Any, *, collection: bool = False
) -> TabletFilter:
    """Make a filter on the name of a record that a tablet relationship refers to."""

    def condition(value: str) -> ColumnElement[bool]:
        if collection:
            return relationship.any(name == value)
        return relationship.has(name == value)

    options = (
        select(name).select_from(Tablet).join(relationship).distinct().order_by(name)
    )
    return TabletFilter(key, label, condition, options)


def _eponym(value: str) -> ColumnElement[bool]:
    return or_(
        Tablet.eponym.has(Eponym.name == value),
        Tablet.year.has(Year.eponym.has(Eponym.name == value)),
    )


def _sent_from(value: str) -> ColumnElement[bool]:
    return Tablet.sent_from.has(Correspondent.name == value)


def _sent_to(value: str) -> ColumnElement[bool]:
    return Tablet.recipients.any(Correspondent.name == value)


def _locality(value: str) -> ColumnElement[bool]:
    return or_(
        Tablet.city.has(City.locality.has(Locality.area == value)),
        Tablet.own_locality.has(Locality.area == value),
    )


_locality_names = (
    select(Locality.area)
    .where(
        or_(
            Locality.id.in_(
                select(City.locality_id).join(Tablet, Tablet.city_id == City.id)
            ),
            Locality.id.in_(select(Tablet.locality_id)),
        )
    )
    .order_by(Locality.area)
)


def _language(value: str) -> ColumnElement[bool]:
    return Tablet.instances.any(Instance.language.has(Language.name == value))


_language_names = (
    select(Language.name)
    .join(Instance, Instance.language_id == Language.id)
    .distinct()
    .order_by(Language.name)
)


def _publication_series() -> dict[int, str]:
    """Return the publication series of each tablet that has one.

    The database stores a publication as text, so the series comes from the
    parser, not from SQL.
    """
    query = select(Tablet.id, Tablet.publication).where(Tablet.publication.is_not(None))
    return {
        tablet_id: series
        for tablet_id, text in db.session.execute(query)
        if (series := parse_publication(text).series)
    }


def _series(value: str) -> ColumnElement[bool]:
    series = _publication_series()
    return Tablet.id.in_(
        [tablet_id for tablet_id, name in series.items() if name == value]
    )


def _series_names() -> list[str]:
    return sorted(set(_publication_series().values()), key=str.casefold)


FILTERS = (
    _related("period", "Period", Tablet.period, Period.name),
    _related("sub_period", "Sub-period", Tablet.sub_period, SubPeriod.name),
    _related("ruler", "Ruler", Tablet.rulers, Ruler.name, collection=True),
    _related("year", "Year", Tablet.year, Year.year),
    TabletFilter("eponym", "Eponym", _eponym),
    _related("city", "City", Tablet.city, City.name),
    TabletFilter("locality", "Locality", _locality, _locality_names),
    TabletFilter("sent_from", "Sent from", _sent_from),
    TabletFilter("sent_to", "Sent to", _sent_to),
    _related("genre", "Genre", Tablet.genre, Genre.name),
    _related("text_vehicle", "Text vehicle", Tablet.text_vehicle, TextVehicle.name),
    _related("function", "Function", Tablet.function, Function.name),
    TabletFilter("language", "Language", _language, _language_names),
    _related("script_type", "Script type", Tablet.script_type, ScriptType.script),
    _related("medium", "Medium", Tablet.medium, Medium.name),
    _related("method", "Method", Tablet.method, Method.name),
    TabletFilter("series", "Series", _series, _series_names),
)
FILTERS_BY_KEY = {tablet_filter.key: tablet_filter for tablet_filter in FILTERS}


def active_filters(args: Mapping[str, str]) -> dict[str, str]:
    """Return the filter values in a query string, in the order of FILTERS."""
    return {f.key: value for f in FILTERS if (value := args.get(f.key, "").strip())}


def filter_options() -> list[tuple[TabletFilter, list[str]]]:
    """Return the filters for the form, with the names that tablets use.

    Omit a filter if tablets use fewer than two of its names.
    """
    options: list[tuple[TabletFilter, list[str]]] = []
    for tablet_filter in FILTERS:
        if tablet_filter.options is None:
            continue
        names: list[str]
        if isinstance(tablet_filter.options, Select):
            names = list(db.session.scalars(tablet_filter.options))
        else:
            names = tablet_filter.options()
        if len(names) > 1:
            options.append((tablet_filter, names))
    return options
