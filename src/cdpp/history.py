"""Pages that show change sets, and undo a change set.

The history of a record lists the change sets that changed it. Undo records a
new change set that sets the old values again: see ``cdpp.editing.revert``.
"""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from flask import Blueprint, redirect, render_template, request, url_for
from flask.typing import ResponseReturnValue
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from cdpp.db import db
from cdpp.editing import RevertConflict, revert
from cdpp.editor import (
    COMMENT_LENGTH,
    EDITOR_COOKIE,
    EDITOR_COOKIE_AGE,
    NAME_LENGTH,
    single_line,
)
from cdpp.models import (
    Change,
    ChangeSet,
    Function,
    Instance,
    Iteration,
    Language,
    Line,
    Surface,
    TextColumn,
)
from cdpp.views import position_text

bp = Blueprint("history", __name__)

CHANGE_SETS_PER_PAGE = 25
FIELD_LABELS = {
    "surface_id": "Surface",
    "column_id": "Column",
    "line_id": "Line",
    "iteration_id": "Iteration",
    "function_id": "Function",
    "language_id": "Language",
}
NEW_RECORD_LABELS = {
    "column": "New column number",
    "line": "New line number",
    "iteration": "New iteration number",
}
# The lookup record of each reference field, and the attribute that names it.
REFERENCES: dict[str, tuple[type[Any], str]] = {
    "surface_id": (Surface, "name"),
    "column_id": (TextColumn, "number"),
    "line_id": (Line, "number"),
    "iteration_id": (Iteration, "number"),
    "function_id": (Function, "name"),
    "language_id": (Language, "name"),
}
POSITION_TABLES = {"column", "line"}
POSITION_FIELDS = {"column_id", "line_id"}


@dataclass(frozen=True)
class ChangeLine:
    """One change of a change set, as the pages show it.

    ``old`` is None for a field of a new lookup record.
    """

    subject: str
    subject_url: str | None
    label: str
    old: str | None
    new: str


@dataclass(frozen=True)
class ChangeSetEntry:
    change_set: ChangeSet
    lines: list[ChangeLine]
    undone_by: int | None

    @property
    def can_be_undone(self) -> bool:
        return self.undone_by is None and any(
            line.old is not None for line in self.lines
        )


@bp.app_template_filter("utc_time")
def utc_time(moment: datetime) -> str:
    return f"{moment.day} {moment:%B %Y, %H:%M} UTC"


def value_text(field: str, value: Any) -> str:
    """Return a field value as the pages show it, for example a line number."""
    if value is None:
        return "not recorded"
    reference = REFERENCES.get(field)
    if reference is None:
        return str(value)
    model, attribute = reference
    record = db.session.get(model, value)
    if record is None:
        return f"missing record {value}"
    text = getattr(record, attribute)
    return position_text(text) if field in POSITION_FIELDS else text


def change_line(change: Change) -> ChangeLine:
    if change.kind == "insert":
        new = str(change.new_value)
        if change.table_name in POSITION_TABLES:
            new = position_text(new)
        label = NEW_RECORD_LABELS.get(change.table_name, f"New {change.table_name}")
        return ChangeLine("", None, label, None, new)

    subject, subject_url = f"{change.table_name} {change.record_id}", None
    if change.table_name == "instance":
        instance = db.session.get(Instance, change.record_id)
        if instance is not None:
            sign, tablet = instance.sign.sign_ref, instance.tablet.museum_number
            subject = f"Instance of {sign} on {tablet}"
            subject_url = url_for("history.instance_history", instance_id=instance.id)
    return ChangeLine(
        subject,
        subject_url,
        FIELD_LABELS.get(change.field, change.field),
        value_text(change.field, change.old_value),
        value_text(change.field, change.new_value),
    )


def entries(change_sets: Sequence[ChangeSet]) -> list[ChangeSetEntry]:
    """Describe ``change_sets``. Load their changes first."""
    ids = [change_set.id for change_set in change_sets]
    undone_by = {
        reverted: undo
        for reverted, undo in db.session.execute(
            select(ChangeSet.reverts_id, ChangeSet.id).where(
                ChangeSet.reverts_id.in_(ids)
            )
        )
    }
    return [
        ChangeSetEntry(
            change_set,
            [change_line(change) for change in change_set.changes],
            undone_by.get(change_set.id),
        )
        for change_set in change_sets
    ]


@bp.get("/changes")
def changes() -> ResponseReturnValue:
    page = db.paginate(
        select(ChangeSet)
        .options(selectinload(ChangeSet.changes))
        .order_by(ChangeSet.id.desc()),
        page=request.args.get("page", 1, type=int),
        per_page=CHANGE_SETS_PER_PAGE,
    )
    return render_template("changes.html", page=page, entries=entries(page.items))


@bp.get("/instances/<int:instance_id>/history")
def instance_history(instance_id: int) -> ResponseReturnValue:
    instance = db.get_or_404(Instance, instance_id)
    changed = select(Change.change_set_id).where(
        Change.table_name == "instance", Change.record_id == instance_id
    )
    change_sets = db.session.scalars(
        select(ChangeSet)
        .where(ChangeSet.id.in_(changed))
        .options(selectinload(ChangeSet.changes))
        .order_by(ChangeSet.id.desc())
    ).all()
    return render_template(
        "instance_history.html", instance=instance, entries=entries(change_sets)
    )


@bp.get("/changes/<int:change_set_id>")
def change_set(change_set_id: int) -> ResponseReturnValue:
    return change_set_page(
        change_set_id, author=request.cookies.get(EDITOR_COOKIE, ""), comment=""
    )


@bp.post("/changes/<int:change_set_id>/undo")
def undo(change_set_id: int) -> ResponseReturnValue:
    original = db.get_or_404(ChangeSet, change_set_id)
    author = single_line(request.form.get("author", ""))
    comment = single_line(request.form.get("comment", ""))
    errors = {}
    if not author:
        errors["author"] = "Enter your name. The history shows who made each change."
    elif len(author) > NAME_LENGTH:
        errors["author"] = f"Enter a name of {NAME_LENGTH} characters or fewer."
    if len(comment) > COMMENT_LENGTH:
        errors["comment"] = f"Enter a comment of {COMMENT_LENGTH} characters or fewer."
    if errors:
        return change_set_page(
            change_set_id, author=author, comment=comment, errors=errors, status=422
        )

    try:
        undo_set = revert(original, author=author, comment=comment or None)
    except RevertConflict as conflict:
        db.session.rollback()
        return change_set_page(
            change_set_id,
            author=author,
            comment=comment,
            conflict=[change_line(change) for change in conflict.changes],
            status=409,
        )
    response = redirect(
        url_for("history.change_set", change_set_id=undo_set.id, undone=change_set_id),
        303,
    )
    response.set_cookie(
        EDITOR_COOKIE,
        author,
        max_age=EDITOR_COOKIE_AGE,
        httponly=True,
        samesite="Lax",
    )
    return response


def change_set_page(
    change_set_id: int,
    *,
    author: str,
    comment: str,
    errors: Mapping[str, str] | None = None,
    conflict: Sequence[ChangeLine] = (),
    status: int = 200,
) -> ResponseReturnValue:
    # The session can hold the change set without its changes already, so load
    # them again.
    change_set = db.first_or_404(
        select(ChangeSet)
        .where(ChangeSet.id == change_set_id)
        .options(selectinload(ChangeSet.changes))
        .execution_options(populate_existing=True)
    )
    return render_template(
        "change_set.html",
        entry=entries([change_set])[0],
        author=author,
        comment=comment,
        errors=errors or {},
        conflict=conflict,
        undone=request.args.get("undone", type=int),
    ), status
