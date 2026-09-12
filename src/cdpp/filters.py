"""Filters for the tablet list.

Each filter selects the tablets that have a related record with a given name.
Tablet pages link to filtered lists, and the tablet list has a filter form.
"""

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Any

from sqlalchemy import ColumnElement, Select, or_, select

from cdpp.db import db
from cdpp.models import (
    City,
    Correspondent,
    Dynasty,
    Eponym,
    Function,
    Genre,
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


@dataclass(frozen=True)
class TabletFilter:
    key: str
    label: str
    condition: Callable[[str], ColumnElement[bool]]
    # The names that the filter form offers. None if only links use the filter.
    options: Select[tuple[str]] | None = None


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
    return or_(
        Tablet.sent_to.has(Correspondent.name == value),
        Tablet.recipients.any(Correspondent.name == value),
    )


FILTERS = (
    _related("period", "Period", Tablet.period, Period.name),
    _related("sub_period", "Sub-period", Tablet.sub_period, SubPeriod.name),
    _related("dynasty", "Dynasty", Tablet.dynasty, Dynasty.name),
    _related("ruler", "Ruler", Tablet.rulers, Ruler.name, collection=True),
    _related("year", "Year", Tablet.year, Year.year),
    TabletFilter("eponym", "Eponym", _eponym),
    _related("city", "City", Tablet.city, City.name),
    _related("locality", "Locality", Tablet.locality, Locality.area),
    TabletFilter("sent_from", "Sent from", _sent_from),
    TabletFilter("sent_to", "Sent to", _sent_to),
    _related("genre", "Genre", Tablet.genre, Genre.name),
    _related("text_vehicle", "Text vehicle", Tablet.text_vehicle, TextVehicle.name),
    _related("function", "Function", Tablet.function, Function.name),
    _related("language", "Language", Tablet.language, Language.name),
    _related("script_type", "Script type", Tablet.script_type, ScriptType.script),
    _related("medium", "Medium", Tablet.medium, Medium.name),
    _related("method", "Method", Tablet.method, Method.name),
)
FILTERS_BY_KEY = {tablet_filter.key: tablet_filter for tablet_filter in FILTERS}


def active_filters(args: Mapping[str, str]) -> dict[str, str]:
    """Return the filter values in a query string, in the order of FILTERS."""
    return {f.key: value for f in FILTERS if (value := args.get(f.key, "").strip())}


def filter_options() -> list[tuple[TabletFilter, list[str]]]:
    """Return the filters for the form, with the names that tablets use.

    Omit a filter if tablets use fewer than two of its names.
    """
    options = []
    for tablet_filter in FILTERS:
        if tablet_filter.options is None:
            continue
        names = list(db.session.scalars(tablet_filter.options))
        if len(names) > 1:
            options.append((tablet_filter, names))
    return options
