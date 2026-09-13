"""Pages of the CDPP site."""

import random
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from itertools import groupby
from pathlib import Path
from typing import Any

from flask import (
    Blueprint,
    Response,
    current_app,
    make_response,
    render_template,
    request,
    send_from_directory,
    url_for,
)
from flask.typing import ResponseReturnValue
from sqlalchemy import func, select
from sqlalchemy.orm import contains_eager, joinedload, selectinload
from werkzeug.exceptions import HTTPException

from cdpp.db import db
from cdpp.filters import FILTERS_BY_KEY, active_filters, filter_options
from cdpp.models import (
    NAME_SOURCES,
    Cdp,
    Correspondent,
    Entity,
    Instance,
    OraccSign,
    Sign,
    SignList,
    SignListEntry,
    Tablet,
)
from cdpp.oracc import list_number_urls, oracc_page_url, signs_named
from cdpp.search import SearchResults, search_records

bp = Blueprint("cdpp", __name__)

SIGNS_PER_PAGE = 120
TABLETS_PER_PAGE = 25
SPECIMENS_ON_HOME_PAGE = 18
SEARCH_LIMIT = 50
IMAGE_MAX_AGE = 60 * 60 * 24 * 30

# Cdp attributes and their column headings, in display order.
CDP_FIELDS = (
    ("form_name", "Form"),
    ("variant_name", "Variant"),
    ("form_description", "Form description"),
    ("description", "Description"),
    ("oracc", "ORACC"),
    ("cdli", "CDLI archaic"),
    ("notes", "Notes"),
)
# Headings of the columns that contain sign names.
SIGN_NAME_HEADINGS = frozenset({"Description", "ORACC", "CDLI archaic"})
# The working notes of the editor of the instance data. A tablet page can hide
# them.
JJT_NOTES_HEADING = "JJT notes (2012)"
INSTANCE_HEADINGS = [
    "Sign",
    "Surface",
    "Column",
    "Line",
    "Function",
    "Iteration",
    "Language",
    JJT_NOTES_HEADING,
    "Notes",
]

type DetailValues = list[tuple[str, str | None]]


@dataclass(frozen=True)
class Detail:
    """An entry in the list of tablet details.

    Each value has the key of a tablet filter, or None. A value with a key
    links to the tablet list, filtered by that value.
    """

    label: str
    values: DetailValues


# Template helpers


@bp.app_template_filter("thousands")
def thousands(number: int) -> str:
    return f"{number:,}"


@bp.app_template_global()
def count_noun(count: int, singular: str, plural: str | None = None) -> str:
    noun = singular if count == 1 else (plural or f"{singular}s")
    return f"{count:,} {noun}"


@bp.app_template_global()
def page_url(page: int) -> str:
    """Return the URL of the current page, with a different page number."""
    args: dict[str, Any] = {
        **(request.view_args or {}),
        **request.args.to_dict(),
        "page": page,
    }
    return url_for(request.endpoint or "cdpp.index", **args)


@bp.app_template_global()
def image_url(instance: Instance) -> str:
    return url_for("cdpp.instance_image", filename=f"{instance.filename}.jpg")


def position_text(number: str) -> str:
    """Return a column or line number as pages show it, as in "1′" for "01'"."""
    text = number.lstrip("0")
    if number.startswith("0") and not text[:1].isdigit():
        text = f"0{text}"
    return text.replace("'", "′")


@bp.app_template_global()
def instance_location(instance: Instance) -> str:
    """Describe where an instance is on its tablet, as in "Obverse, line 3".

    The description contains only recorded values, not defaults.
    """
    parts = []
    if instance.surface is not None:
        parts.append(instance.surface.name)
    if instance.column is not None:
        parts.append(f"column {position_text(instance.column.number)}")
    if instance.line is not None:
        parts.append(f"line {position_text(instance.line.number)}")
    text = ", ".join(parts)
    return text[:1].upper() + text[1:]


# Pages


@bp.get("/")
def index() -> ResponseReturnValue:
    count = select(func.count())
    stats = {
        "tablets": db.session.scalar(count.select_from(Tablet)) or 0,
        "signs": db.session.scalar(count.select_from(Sign)) or 0,
        "instances": db.session.scalar(count.select_from(Instance)) or 0,
    }
    return render_page(
        "index.html",
        partial="_specimens.html",
        target="specimens",
        stats=stats,
        specimens=random_specimens(SPECIMENS_ON_HOME_PAGE),
    )


@bp.get("/signs")
def signs() -> ResponseReturnValue:
    with_images = request.args.get("with_images") == "1"
    statement = select(Sign).order_by(Sign.sign_ref)
    if with_images:
        statement = statement.where(Sign.instances.any())
    page = db.paginate(
        statement,
        page=request.args.get("page", 1, type=int),
        per_page=SIGNS_PER_PAGE,
    )
    count = select(func.count())
    return render_template(
        "signs.html",
        page=page,
        with_images=with_images,
        counts=instance_counts(Instance.sign_id, [sign.id for sign in page.items]),
        total=db.session.scalar(count.select_from(Sign)) or 0,
        total_with_images=db.session.scalar(
            select(func.count(func.distinct(Instance.sign_id)))
        )
        or 0,
    )


@bp.get("/signs/<int:sign_id>")
def sign(sign_id: int) -> ResponseReturnValue:
    sign = db.get_or_404(
        Sign,
        sign_id,
        options=[
            selectinload(Sign.cdp_records).options(
                selectinload(Cdp.names),
                selectinload(Cdp.sign_list_entries).joinedload(SignListEntry.sign_list),
            )
        ],
    )
    tablets = (
        db.session.execute(
            select(Tablet, func.count(Instance.id))
            .join(Tablet.instances)
            .where(Instance.sign_id == sign_id)
            .group_by(Tablet.id)
            .order_by(Tablet.museum_number)
        )
        .tuples()
        .all()
    )
    specimens = db.session.scalars(
        select(Instance)
        .where(Instance.sign_id == sign_id)
        .options(joinedload(Instance.tablet), joinedload(Instance.sign))
        .order_by(Instance.id)
        .limit(6)
    ).all()
    sign_lists = db.session.scalars(select(SignList).order_by(SignList.position)).all()
    records = sign.cdp_records
    number_urls = list_number_urls(
        [entry for record in records for entry in record.sign_list_entries]
    )
    oracc_signs = signs_named(
        name for record in records if (name := record.name_from("oracc"))
    )
    headings, rows = omit_empty_columns(
        [heading for _, heading in CDP_FIELDS]
        + [sign_list.name for sign_list in sign_lists],
        [
            record_cells(record, sign_lists, number_urls, oracc_signs)
            for record in records
        ],
    )
    return render_template(
        "sign.html",
        sign=sign,
        tablets=tablets,
        instance_count=sum(count for _, count in tablets),
        specimens=specimens,
        headings=headings,
        rows=rows,
        sign_name_headings=SIGN_NAME_HEADINGS,
    )


@bp.get("/signs/<int:sign_id>/images")
def sign_images(sign_id: int) -> ResponseReturnValue:
    sign = db.get_or_404(Sign, sign_id)
    instances = list(
        db.session.scalars(
            select(Instance)
            .join(Instance.tablet)
            .where(Instance.sign_id == sign_id)
            .options(
                contains_eager(Instance.tablet),
                joinedload(Instance.surface),
                joinedload(Instance.column),
                joinedload(Instance.line),
                joinedload(Instance.function),
            )
            .order_by(Tablet.museum_number, Instance.id)
        )
    )
    groups = [
        (tablet, list(items))
        for tablet, items in groupby(instances, key=lambda i: i.tablet)
    ]
    return render_template(
        "sign_images.html",
        sign=sign,
        groups=groups,
        instance_count=len(instances),
    )


@bp.get("/tablets")
def tablets() -> ResponseReturnValue:
    active = active_filters(request.args)
    statement = (
        select(Tablet)
        .where(*(FILTERS_BY_KEY[key].condition(value) for key, value in active.items()))
        .options(
            joinedload(Tablet.period),
            joinedload(Tablet.medium),
            joinedload(Tablet.city),
        )
        .order_by(Tablet.museum_number)
    )
    page = db.paginate(
        statement,
        page=request.args.get("page", 1, type=int),
        per_page=TABLETS_PER_PAGE,
    )
    if page.total:
        status = f"Tablets {page.first} to {page.last} of {page.total:,}."
    else:
        status = "No tablets match these filters."
    options = [] if htmx_target() == "tablet-results" else filter_options()
    removals = []
    for key, value in active.items():
        remaining: dict[str, Any] = {k: v for k, v in active.items() if k != key}
        url = url_for("cdpp.tablets", **remaining)
        removals.append((FILTERS_BY_KEY[key].label, value, url))
    return render_page(
        "tablets.html",
        partial="_tablet_results.html",
        target="tablet-results",
        page=page,
        status=status,
        active=active,
        removals=removals,
        options=options,
        form_keys={tablet_filter.key for tablet_filter, _ in options},
        counts=instance_counts(Instance.tablet_id, [t.id for t in page.items]),
    )


@bp.get("/tablets/<int:tablet_id>")
def tablet(tablet_id: int) -> ResponseReturnValue:
    tablet = db.get_or_404(
        Tablet,
        tablet_id,
        options=[
            selectinload(Tablet.rulers),
            selectinload(Tablet.recipients).options(
                joinedload(Correspondent.ruler),
                joinedload(Correspondent.non_ruler),
            ),
        ],
    )
    table = instance_table(tablet_id, show_notes=request.args.get("notes") != "hide")
    instances = table["instances"]
    return render_page(
        "tablet.html",
        partial="_tablet_instances.html",
        target="tablet-instances",
        tablet=tablet,
        details=tablet_details(tablet),
        instance_count=len(instances),
        sign_count=len({instance.sign_id for instance in instances}),
        specimens=random.sample(instances, k=min(4, len(instances))),
        **table,
    )


def instance_table(tablet_id: int, *, show_notes: bool) -> dict[str, Any]:
    """Return the context of the table of instances on a tablet page."""
    instances = tablet_instances(tablet_id)
    headings = INSTANCE_HEADINGS
    rows = [instance_row(instance) for instance in instances]
    if not show_notes:
        notes_column = INSTANCE_HEADINGS.index(JJT_NOTES_HEADING)
        headings = [h for i, h in enumerate(headings) if i != notes_column]
        rows = [[v for i, v in enumerate(row) if i != notes_column] for row in rows]
    headings, rows = omit_empty_columns(headings, rows)
    return {
        "instances": instances,
        "instance_ids": [instance.id for instance in instances],
        "show_notes": show_notes,
        "note_count": sum(1 for instance in instances if instance.jjt_notes),
        "headings": headings,
        "rows": rows,
        "has_defaults": any(
            isinstance(value, Position) and value.default
            for row in rows
            for value in row
        ),
    }


@bp.get("/tablets/<int:tablet_id>/images")
def tablet_images(tablet_id: int) -> ResponseReturnValue:
    tablet = db.get_or_404(Tablet, tablet_id)
    instances = tablet_instances(tablet_id)
    groups = [
        (sign, list(items)) for sign, items in groupby(instances, key=lambda i: i.sign)
    ]
    return render_template(
        "tablet_images.html",
        tablet=tablet,
        groups=groups,
        instance_count=len(instances),
    )


@bp.get("/search")
def search() -> ResponseReturnValue:
    query = request.args.get("q", "").strip()
    results: SearchResults | None = None
    signs: list[Sign] = []
    tablets: list[Tablet] = []
    if query:
        results = search_records(query, limit=SEARCH_LIMIT)
        signs = in_rank_order(Sign, results.sign_ids)
        tablets = in_rank_order(
            Tablet,
            results.tablet_ids,
            joinedload(Tablet.period),
            joinedload(Tablet.medium),
            joinedload(Tablet.city),
        )
    return render_page(
        "search.html",
        partial="_search_results.html",
        target="search-results",
        query=query,
        signs=signs,
        tablets=tablets,
        status=search_status(query, results),
    )


@bp.get("/media/instance/<path:filename>")
def instance_image(filename: str) -> Response:
    return send_from_directory(media_root(), filename, max_age=IMAGE_MAX_AGE)


# Errors


@bp.app_errorhandler(404)
def not_found(_error: HTTPException) -> ResponseReturnValue:
    return render_template(
        "error.html",
        title="Page not found",
        message="There is no page at this address.",
    ), 404


@bp.app_errorhandler(500)
def server_error(_error: Exception) -> ResponseReturnValue:
    return render_template(
        "error.html",
        title="Server error",
        message="The server could not show this page. Try again later.",
    ), 500


# Queries and presentation


def htmx_target() -> str | None:
    """Return the ID of the element that an htmx request replaces.

    Return None for a request that needs a full page. This includes a boosted
    request, which replaces the body, and a history restore.
    """
    if request.headers.get("HX-Request") != "true":
        return None
    if request.headers.get("HX-History-Restore-Request") == "true":
        return None
    return request.headers.get("HX-Target")


def render_page(
    template: str,
    *,
    partial: str,
    target: str,
    status_code: int = 200,
    **context: Any,
) -> Response:
    """Render ``partial`` if an htmx request replaces ``target``, else ``template``."""
    is_partial = htmx_target() == target
    response = make_response(
        render_template(partial if is_partial else template, oob=is_partial, **context),
        status_code,
    )
    response.vary.update(("HX-Request", "HX-Target"))
    return response


def media_root() -> Path:
    return Path(current_app.config["MEDIA_ROOT"]) / "instance"


def random_specimens(limit: int) -> list[Instance]:
    """Return instances in random order, omitting those without an image file."""
    candidates = db.session.scalars(
        select(Instance)
        .options(joinedload(Instance.sign), joinedload(Instance.tablet))
        .order_by(func.random())
        .limit(limit * 2)
    )
    root = media_root()
    return [i for i in candidates if (root / f"{i.filename}.jpg").is_file()][:limit]


def instance_counts(column: Any, ids: list[int]) -> dict[int, int]:
    """Count the instances for each ID, grouped by ``column``."""
    if not ids:
        return {}
    rows = db.session.execute(
        select(column, func.count()).where(column.in_(ids)).group_by(column)
    )
    return dict(rows.tuples().all())


def in_rank_order[M: Entity](model: type[M], ids: list[int], *options: Any) -> list[M]:
    """Load the records with ``ids``, in the order of ``ids``."""
    if not ids:
        return []
    records = db.session.scalars(
        select(model).where(model.id.in_(ids)).options(*options)
    )
    by_id = {record.id: record for record in records}
    return [by_id[record_id] for record_id in ids if record_id in by_id]


def tablet_instances(tablet_id: int) -> list[Instance]:
    return list(
        db.session.scalars(
            select(Instance)
            .join(Instance.sign)
            .where(Instance.tablet_id == tablet_id)
            .options(
                contains_eager(Instance.sign),
                joinedload(Instance.surface),
                joinedload(Instance.column),
                joinedload(Instance.line),
                joinedload(Instance.function),
                joinedload(Instance.iteration),
                joinedload(Instance.language),
            )
            .order_by(Sign.sign_ref, Instance.id)
        )
    )


def omit_empty_columns[T](
    headings: list[str], rows: list[list[T]]
) -> tuple[list[str], list[list[T]]]:
    """Remove the columns that have no value in any row."""
    keep = [i for i in range(len(headings)) if any(row[i] for row in rows)]
    return [headings[i] for i in keep], [[row[i] for i in keep] for row in rows]


@dataclass(frozen=True)
class Cell:
    """A table cell. ``url`` leads to the Oracc Sign List, ``ebl_url`` to eBL."""

    text: str
    url: str | None = None
    ebl_url: str | None = None

    def __bool__(self) -> bool:
        return bool(self.text)


def record_cells(
    record: Cdp,
    sign_lists: Sequence[SignList],
    number_urls: Mapping[int, str],
    oracc_signs: Mapping[str, OraccSign],
) -> list[Cell]:
    """Return the cells of a CDP record: one for each of CDP_FIELDS, then one
    for each of ``sign_lists``."""
    cells = []
    for field, _ in CDP_FIELDS:
        if field == "oracc":
            name = record.name_from("oracc") or ""
            oracc_sign = oracc_signs.get(name)
            if oracc_sign is None:
                cells.append(Cell(name))
            else:
                url = oracc_page_url(oracc_sign.oid)
                cells.append(Cell(name, url, oracc_sign.ebl_url))
        elif field in NAME_SOURCES:
            cells.append(Cell(record.name_from(field) or ""))
        else:
            cells.append(Cell(getattr(record, field) or ""))
    entries = {entry.sign_list_id: entry for entry in record.sign_list_entries}
    for sign_list in sign_lists:
        entry = entries.get(sign_list.id)
        if entry is None:
            cells.append(Cell(""))
        else:
            cells.append(Cell(entry.number, number_urls.get(entry.id)))
    return cells


# Pages show these values when an instance has no surface, column or iteration.
# The database does not store them. See docs/schema-and-data-questions.md.
DEFAULT_SURFACE = "obv"
DEFAULT_COLUMN = "i"
DEFAULT_ITERATION = "1"


@dataclass(frozen=True)
class Position:
    """A surface, column or iteration value in a table of instances.

    The data do not contain a default. A table column that has only defaults
    is empty.
    """

    text: str
    default: bool = False

    def __bool__(self) -> bool:
        return bool(self.text) and not self.default

    def __str__(self) -> str:
        return self.text


def position(value: str | None, default: str) -> Position:
    return Position(value) if value else Position(default, default=True)


def instance_row(instance: Instance) -> list[Any]:
    return [
        instance.sign,
        position(instance.surface.name if instance.surface else None, DEFAULT_SURFACE),
        position(
            position_text(instance.column.number) if instance.column else None,
            DEFAULT_COLUMN,
        ),
        position_text(instance.line.number) if instance.line else "",
        instance.function.name if instance.function else "",
        position(
            instance.iteration.number if instance.iteration else None,
            DEFAULT_ITERATION,
        ),
        instance.language.name if instance.language else "",
        instance.jjt_notes or "",
        instance.notes or "",
    ]


def tablet_details(tablet: Tablet) -> list[Detail]:
    eponym = tablet.eponym or (tablet.year.eponym if tablet.year else None)
    recipients = [*tablet.recipients, *([tablet.sent_to] if tablet.sent_to else [])]
    sender = tablet.sent_from.name if tablet.sent_from else None
    entries: list[tuple[str, DetailValues]] = [
        (
            "Ruler" if len(tablet.rulers) == 1 else "Rulers",
            [(ruler.name, "ruler") for ruler in tablet.rulers],
        ),
        ("Period", [(tablet.period.name, "period")]),
        (
            "Sub-period",
            _linked(tablet.sub_period and tablet.sub_period.name, "sub_period"),
        ),
        ("Dynasty", _linked(tablet.dynasty and tablet.dynasty.name, "dynasty")),
        ("Year", _linked(tablet.year and tablet.year.year, "year")),
        ("Month", _plain(tablet.absolute_month)),
        ("Day", _plain(tablet.absolute_day)),
        ("Eponym", _linked(eponym and eponym.name, "eponym")),
        ("Ancient year", _plain(tablet.ancient_year)),
        ("Ancient month", _plain(tablet.ancient_month)),
        ("Ancient day", _plain(tablet.ancient_day)),
        ("City", _linked(tablet.city and tablet.city.name, "city")),
        ("City site", _plain(tablet.city_site and tablet.city_site.name)),
        ("Origin city", _plain(tablet.origin_city and tablet.origin_city.name)),
        ("Locality", _linked(tablet.locality and tablet.locality.area, "locality")),
        ("Sub-locality", _plain(tablet.sub_locality and tablet.sub_locality.name)),
        ("Sent from", _linked(sender, "sent_from")),
        (
            "Sent to",
            [(name, "sent_to") for recipient in recipients if (name := recipient.name)],
        ),
        (
            "Text vehicle",
            _linked(tablet.text_vehicle and tablet.text_vehicle.name, "text_vehicle"),
        ),
        ("Genre", _linked(tablet.genre and tablet.genre.name, "genre")),
        ("Function", _linked(tablet.function and tablet.function.name, "function")),
        ("Language", _linked(tablet.language and tablet.language.name, "language")),
        (
            "Script type",
            _linked(tablet.script_type and tablet.script_type.script, "script_type"),
        ),
        ("Medium", [(tablet.medium.name, "medium")]),
        ("Method", _linked(tablet.method and tablet.method.name, "method")),
        ("Scribe", _plain(tablet.author and tablet.author.name)),
        ("Publication", _plain(tablet.publication)),
        ("Notes", _plain(tablet.notes)),
    ]
    return [Detail(label, values) for label, values in entries if values]


def _linked(text: object, key: str) -> DetailValues:
    return [(text, key)] if isinstance(text, str) and text else []


def _plain(text: object) -> DetailValues:
    return [(text, None)] if isinstance(text, str) and text else []


def search_status(query: str, results: SearchResults | None) -> str:
    if not query:
        return ""
    if results is None or not (results.sign_count or results.tablet_count):
        return f"No signs or tablets match “{query}”."
    counts = [(results.sign_count, "sign"), (results.tablet_count, "tablet")]
    parts = [count_noun(count, noun) for count, noun in counts if count]
    verb = "matches" if sum(count for count, _ in counts) == 1 else "match"
    status = f"{' and '.join(parts)} {verb} “{query}”."
    if max(results.sign_count, results.tablet_count) > SEARCH_LIMIT:
        status += f" The first {SEARCH_LIMIT} of each are shown."
    return status
