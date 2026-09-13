"""The page of a sign instance: its photograph, its position and its tablet."""

import re
from typing import Any

from flask import Blueprint, render_template, request
from flask.typing import ResponseReturnValue
from sqlalchemy import select
from sqlalchemy.orm import joinedload, selectinload

from cdpp.db import db
from cdpp.images import image_size
from cdpp.models import Change, ChangeSet, Correspondent, Instance, Period, Tablet
from cdpp.oracc import sign_glyphs
from cdpp.views import (
    DEFAULT_COLUMN,
    DEFAULT_ITERATION,
    DEFAULT_SURFACE,
    JJT_NOTES_HEADING,
    media_root,
    position,
    position_text,
    tablet_details,
)

bp = Blueprint("instances", __name__)

SCALES = (1, 2, 4)
DEFAULT_SCALE = 2
SAME_PERIOD_LIMIT = 12
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
    column = instance.column.number if instance.column else DEFAULT_COLUMN
    line = instance.line.number if instance.line else ""
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
            joinedload(Instance.column),
            joinedload(Instance.line),
        )
    )
    return sorted(db.session.scalars(statement), key=key)


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
                position_text(instance.column.number) if instance.column else None,
                DEFAULT_COLUMN,
            ),
        ),
        ("Line", position_text(instance.line.number) if instance.line else ""),
        (
            "Iteration",
            position(
                instance.iteration.number if instance.iteration else None,
                DEFAULT_ITERATION,
            ),
        ),
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
            joinedload(Instance.column),
            joinedload(Instance.line),
            joinedload(Instance.iteration),
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
    scale = request.args.get("scale", DEFAULT_SCALE, type=int)
    if scale not in SCALES:
        scale = DEFAULT_SCALE
    path = media_root() / f"{instance.filename}.jpg"
    size = image_size(path.read_bytes()) if path.is_file() else None

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
        scales=SCALES,
        size=size,
        fields=instance_fields(instance),
        details=details,
        sign_neighbours=neighbours(sign_instances, instance),
        tablet_neighbours=neighbours(tablet_instances, instance),
        same_period=same_period,
        change_set=change_set,
    )
