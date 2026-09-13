"""The page of a sign instance, and comparisons of instances side by side."""

import re
from dataclasses import dataclass
from typing import Any

from flask import Blueprint, redirect, render_template, request, url_for
from flask.typing import ResponseReturnValue
from sqlalchemy import func, select
from sqlalchemy.orm import joinedload, selectinload

from cdpp.db import db
from cdpp.images import image_size
from cdpp.models import (
    Change,
    ChangeSet,
    Correspondent,
    Instance,
    Period,
    Sign,
    Tablet,
)
from cdpp.oracc import sign_glyphs
from cdpp.views import (
    DEFAULT_COLUMN,
    DEFAULT_ITERATION,
    DEFAULT_SURFACE,
    JJT_NOTES_HEADING,
    in_rank_order,
    media_root,
    position,
    position_text,
    tablet_details,
)

bp = Blueprint("instances", __name__)

SCALES = (1, 2, 4)
DEFAULT_SCALE = 2
SAME_PERIOD_LIMIT = 12
COMPARISON_LIMIT = 12
# The tablet details that the instance page shows.
TABLET_LABELS = frozenset(
    {
        "Ruler",
        "Rulers",
        "Period",
        "Sub-period",
        "Year",
        "Eponym",
        "City",
        "Locality",
        "Genre",
        "Script type",
        "Publication",
    }
)
# The obverse comes before the reverse. Other surfaces come after both.
SURFACE_ORDER = {"obv": 0, "rev": 1}
ROMAN_VALUES = {"i": 1, "v": 5, "x": 10, "l": 50}
YEAR_RE = re.compile(r"(\d+)\s*(BC|AD)", re.IGNORECASE)
LEADING_NUMBER_RE = re.compile(r"\d+")


def period_start(period: Period) -> int:
    """Return the first year of ``period``, negative for BC, or 0 if it is not known."""
    match = YEAR_RE.search(period.from_date or "")
    if match is None:
        return 0
    year = int(match[1])
    return -year if match[2].upper() == "BC" else year


def roman_number(text: str) -> int:
    """Return the value of a column number in Roman numerals, as in 2 for "ii'"."""
    values = [ROMAN_VALUES[char] for char in text.lower() if char in ROMAN_VALUES]
    total = 0
    for index, value in enumerate(values):
        following = values[index + 1] if index + 1 < len(values) else 0
        total += -value if value < following else value
    return total


def position_key(instance: Instance) -> tuple[Any, ...]:
    """Return a sort key for the position of an instance on its tablet.

    An instance without a surface or a column sorts with the default value.
    """
    surface = instance.surface.name if instance.surface else DEFAULT_SURFACE
    column = instance.column or DEFAULT_COLUMN
    line = instance.line or ""
    line_number = LEADING_NUMBER_RE.match(line)
    return (
        SURFACE_ORDER.get(surface, len(SURFACE_ORDER)),
        surface,
        roman_number(column),
        column,
        int(line_number[0]) if line_number else 0,
        line,
        instance.id,
    )


def sign_key(instance: Instance) -> tuple[Any, ...]:
    """Return a sort key for the instances of a sign: period, tablet, position."""
    tablet = instance.tablet
    return (
        period_start(tablet.period),
        tablet.period.name,
        tablet.museum_number,
        *position_key(instance),
    )


def neighbours(
    instances: list[Instance], current: Instance
) -> tuple[Instance | None, Instance | None]:
    """Return the instances before and after ``current`` in ``instances``."""
    index = next(i for i, other in enumerate(instances) if other.id == current.id)
    previous = instances[index - 1] if index > 0 else None
    following = instances[index + 1] if index + 1 < len(instances) else None
    return previous, following


def sorted_instances(condition: Any, key: Any) -> list[Instance]:
    statement = (
        select(Instance)
        .where(condition)
        .options(
            joinedload(Instance.sign),
            joinedload(Instance.tablet).joinedload(Tablet.period),
            joinedload(Instance.surface),
        )
    )
    return sorted(db.session.scalars(statement), key=key)


def requested_scale() -> int:
    scale = request.args.get("scale", DEFAULT_SCALE, type=int)
    return scale if scale in SCALES else DEFAULT_SCALE


def photograph_size(instance: Instance) -> tuple[int, int] | None:
    path = media_root() / f"{instance.filename}.jpg"
    return image_size(path.read_bytes()) if path.is_file() else None


def comparison_ids(text: str | None) -> list[int]:
    """Return the IDs in a comma-separated list, in order and without duplicates.

    Ignore values that are not IDs, and the IDs after the first COMPARISON_LIMIT.
    """
    ids: list[int] = []
    for part in (text or "").split(","):
        value = part.strip()
        if value.isascii() and value.isdigit() and int(value) not in ids:
            ids.append(int(value))
    return ids[:COMPARISON_LIMIT]


def instance_page_url(instance_id: int, selection: list[int], scale: int) -> str:
    return url_for(
        "instances.instance",
        instance_id=instance_id,
        compare=",".join(map(str, selection)) or None,
        scale=None if scale == DEFAULT_SCALE else scale,
    )


def comparison_url(ids: list[int], scale: int) -> str:
    return url_for(
        "instances.compare",
        instances=",".join(map(str, ids)) or None,
        scale=None if scale == DEFAULT_SCALE else scale,
    )


@bp.app_template_global()
def instance_url(instance: Instance) -> str:
    """Return the URL of the page of ``instance``.

    A link from an instance page keeps the comparison and the scale of that page.
    """
    if request.endpoint != "instances.instance":
        return url_for("instances.instance", instance_id=instance.id)
    return instance_page_url(
        instance.id, comparison_ids(request.args.get("compare")), requested_scale()
    )


def period_instance_ids(sign_id: int) -> list[int]:
    """Return the lowest instance ID of a sign in each period, in period order."""
    rows = db.session.execute(
        select(Period, func.min(Instance.id))
        .join(Tablet, Tablet.period_id == Period.id)
        .join(Instance, Instance.tablet_id == Tablet.id)
        .where(Instance.sign_id == sign_id)
        .group_by(Period.id)
    ).tuples()
    ordered = sorted(rows, key=lambda row: (period_start(row[0]), row[0].name))
    return [instance_id for _, instance_id in ordered]


@dataclass(frozen=True)
class ComparisonItem:
    instance: Instance
    size: tuple[int, int] | None
    url: str
    remove_url: str


def instance_fields(instance: Instance) -> list[tuple[str, Any]]:
    """Return the label and the value of each field that has a value or a default."""
    fields = [
        ("Function", instance.function.name if instance.function else ""),
        ("Language", instance.language.name if instance.language else ""),
        (
            "Surface",
            position(
                instance.surface.name if instance.surface else None, DEFAULT_SURFACE
            ),
        ),
        (
            "Column",
            position(
                position_text(instance.column) if instance.column else None,
                DEFAULT_COLUMN,
            ),
        ),
        ("Line", position_text(instance.line) if instance.line else ""),
        ("Iteration", position(instance.iteration, DEFAULT_ITERATION)),
        ("Notes", instance.notes or ""),
        (JJT_NOTES_HEADING, instance.jjt_notes or ""),
    ]
    return [(label, value) for label, value in fields if str(value)]


@bp.get("/instances/<int:instance_id>")
def instance(instance_id: int) -> ResponseReturnValue:
    instance = db.get_or_404(
        Instance,
        instance_id,
        options=[
            joinedload(Instance.sign),
            joinedload(Instance.surface),
            joinedload(Instance.function),
            joinedload(Instance.language),
            joinedload(Instance.tablet).options(
                joinedload(Tablet.period),
                selectinload(Tablet.rulers),
                selectinload(Tablet.recipients).options(
                    joinedload(Correspondent.ruler),
                    joinedload(Correspondent.non_ruler),
                ),
            ),
        ],
    )
    scale = requested_scale()
    selection = comparison_ids(request.args.get("compare"))
    if instance.id in selection:
        toggle_label = "Remove from comparison"
        toggled = [other for other in selection if other != instance.id]
    else:
        toggle_label = "Add to comparison"
        toggled = [*selection, instance.id][:COMPARISON_LIMIT]

    sign_instances = sorted_instances(Instance.sign_id == instance.sign_id, sign_key)
    tablet_instances = sorted_instances(
        Instance.tablet_id == instance.tablet_id, position_key
    )
    same_period = [
        other
        for other in sign_instances
        if other.id != instance.id
        and other.tablet.period_id == instance.tablet.period_id
    ][:SAME_PERIOD_LIMIT]
    change_set = db.session.scalars(
        select(ChangeSet)
        .join(ChangeSet.changes)
        .where(Change.table_name == "instance", Change.record_id == instance.id)
        .order_by(ChangeSet.id.desc())
        .limit(1)
    ).first()
    details = [
        detail
        for detail in tablet_details(instance.tablet)
        if detail.label in TABLET_LABELS
    ]
    return render_template(
        "instance.html",
        instance=instance,
        glyph=sign_glyphs([instance.sign_id]).get(instance.sign_id),
        scale=scale,
        scale_links=[
            (option, instance_page_url(instance.id, selection, option))
            for option in SCALES
        ],
        size=photograph_size(instance),
        compare=selection,
        compare_url=comparison_url(selection, scale),
        toggle_label=toggle_label,
        # A full comparison cannot take another instance.
        toggle_url=None
        if toggled == selection
        else instance_page_url(instance.id, toggled, scale),
        fields=instance_fields(instance),
        details=details,
        sign_neighbours=neighbours(sign_instances, instance),
        tablet_neighbours=neighbours(tablet_instances, instance),
        same_period=same_period,
        change_set=change_set,
    )


@bp.get("/compare")
def compare() -> ResponseReturnValue:
    scale = requested_scale()
    sign_id = request.args.get("sign", type=int)
    if sign_id is not None:
        db.get_or_404(Sign, sign_id)
        return redirect(comparison_url(period_instance_ids(sign_id), scale))
    instances = in_rank_order(
        Instance,
        comparison_ids(request.args.get("instances")),
        joinedload(Instance.sign),
        joinedload(Instance.tablet).joinedload(Tablet.period),
        joinedload(Instance.surface),
    )
    ids = [instance.id for instance in instances]
    items = [
        ComparisonItem(
            instance=instance,
            size=photograph_size(instance),
            url=instance_page_url(instance.id, ids, scale),
            remove_url=comparison_url(
                [other for other in ids if other != instance.id], scale
            ),
        )
        for instance in instances
    ]
    return render_template(
        "compare.html",
        items=items,
        scale=scale,
        scale_links=[(option, comparison_url(ids, option)) for option in SCALES],
    )
