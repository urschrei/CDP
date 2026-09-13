"""Pages that edit records.

The site has no sign-in: anyone who can reach it can edit. Each save records a
change set with the name that the editor gives, and a cookie keeps the name
for the next edit.
"""

import re
from collections.abc import Mapping
from typing import Any
from urllib.parse import urlsplit

from flask import (
    Blueprint,
    abort,
    make_response,
    redirect,
    render_template,
    request,
    url_for,
)
from flask.typing import ResponseReturnValue
from sqlalchemy import select

from cdpp.db import db
from cdpp.editing import EditConflict, fingerprint, save
from cdpp.models import (
    Function,
    Instance,
    Language,
    Surface,
)
from cdpp.views import htmx_target, instance_table, position_text

bp = Blueprint("editor", __name__)

EDITOR_COOKIE = "cdpp_editor"
EDITOR_COOKIE_AGE = 60 * 60 * 24 * 365
NAME_LENGTH = 100
COMMENT_LENGTH = 500
# The instance fields that the form edits, in the order of the form.
INSTANCE_FIELDS = (
    "surface_id",
    "column",
    "line",
    "iteration",
    "function_id",
    "language_id",
)
CHOICE_FIELDS = (
    ("surface_id", Surface),
    ("function_id", Function),
    ("language_id", Language),
)
# The data write primes as apostrophes. An editor can type a prime (U+2032), a
# right single quotation mark (U+2019) or a double prime (U+2033).
PRIMES = str.maketrans({"′": "'", "\u2019": "'", "″": "''"})


@bp.before_app_request
def refuse_forms_from_other_sites() -> None:
    """Refuse a form that a page on another site sends to this site."""
    if request.method in ("GET", "HEAD"):
        return
    source = request.headers.get("Origin") or request.headers.get("Referer")
    if source and urlsplit(source).netloc != request.host:
        abort(403)


# Values of the form


def compact(text: str) -> str:
    return "".join(text.translate(PRIMES).split())


def line_number(text: str) -> str:
    """Return a line number as the data write it, as in "03'" for "3′"."""
    match = re.fullmatch(r"(\d{1,3})('{0,2})", compact(text))
    if match is None:
        raise ValueError("Enter a line number, for example 3 or 3′.")
    return f"{int(match[1]):02d}{match[2]}"


def column_number(text: str) -> str:
    """Return a column number as the data write it, as in "ii'" for "II′"."""
    number = compact(text).lower()
    if re.fullmatch(r"[ivxl]+'{0,2}", number) is None or len(number) > 5:
        raise ValueError("Enter a column in Roman numerals, for example ii or ii′.")
    return number


def iteration_number(text: str) -> str:
    number = compact(text)
    if re.fullmatch(r"[1-9]\d?", number) is None:
        raise ValueError("Enter an iteration from 1 to 99.")
    return number


def single_line(text: str) -> str:
    return " ".join(text.split())


def current_values(instance: Instance) -> dict[str, str]:
    """Return the values of the form for ``instance``, as the editor sees them."""
    return {
        "surface_id": str(instance.surface_id or ""),
        "column": position_text(instance.column) if instance.column else "",
        "line": position_text(instance.line) if instance.line else "",
        "iteration": instance.iteration or "",
        "function_id": str(instance.function_id or ""),
        "language_id": str(instance.language_id or ""),
    }


def parse_instance_form(
    form: Mapping[str, str],
) -> tuple[dict[str, Any], dict[str, str]]:
    """Return the new field values and the errors."""
    values: dict[str, Any] = {}
    errors: dict[str, str] = {}
    for field, model in CHOICE_FIELDS:
        choice = form.get(field, "")
        if not choice:
            values[field] = None
        elif choice.isdigit() and db.session.get(model, int(choice)) is not None:
            values[field] = int(choice)
        else:
            errors[field] = "Choose a value from the list."

    numbered = (
        ("column", column_number),
        ("line", line_number),
        ("iteration", iteration_number),
    )
    for name, parse in numbered:
        text = form.get(name, "")
        if not text.strip():
            values[name] = None
            continue
        try:
            values[name] = parse(text)
        except ValueError as error:
            errors[name] = str(error)
    return values, errors


def lookup_options() -> dict[str, list[tuple[int, str]]]:
    return {
        field: [
            (record.id, record.name)
            for record in db.session.scalars(select(model).order_by(model.name))
        ]
        for field, model in CHOICE_FIELDS
    }


# Pages


@bp.route("/instances/<int:instance_id>/edit", methods=["GET", "POST"])
def edit_instance(instance_id: int) -> ResponseReturnValue:
    instance = db.get_or_404(Instance, instance_id)
    show_notes = request.values.get("notes") != "hide"
    columns = request.values.get("columns", default=1, type=int)
    if request.method == "GET":
        return instance_form(
            instance,
            values=current_values(instance),
            author=request.cookies.get(EDITOR_COOKIE, ""),
            comment="",
            show_notes=show_notes,
            columns=columns,
            inline=htmx_target() == f"instance-{instance.id}",
        )

    inline = htmx_target() == "tablet-instances"
    form = request.form
    values, errors = parse_instance_form(form)
    author = single_line(form.get("author", ""))
    comment = single_line(form.get("comment", ""))
    if not author:
        errors["author"] = "Enter your name. The history shows who made each change."
    elif len(author) > NAME_LENGTH:
        errors["author"] = f"Enter a name of {NAME_LENGTH} characters or fewer."
    if len(comment) > COMMENT_LENGTH:
        errors["comment"] = f"Enter a comment of {COMMENT_LENGTH} characters or fewer."
    submitted = {name: form.get(name, "") for name in current_values(instance)}

    if errors:
        db.session.rollback()
        return instance_form(
            instance,
            values=submitted,
            author=author,
            comment=comment,
            show_notes=show_notes,
            columns=columns,
            inline=inline,
            errors=errors,
            status=422,
        )
    try:
        change_set = save(
            instance,
            values,
            author=author,
            seen=form.get("seen", ""),
            comment=comment or None,
        )
    except EditConflict:
        instance = db.get_or_404(Instance, instance_id)
        return instance_form(
            instance,
            values=current_values(instance),
            author=author,
            comment=comment,
            show_notes=show_notes,
            columns=columns,
            inline=inline,
            conflict=True,
            status=409,
        )

    sign = instance.sign.sign_ref
    if inline:
        saved = (
            f"Saved the change to this instance of {sign}."
            if change_set
            else f"No values changed for this instance of {sign}."
        )
        response = make_response(
            render_template(
                "_tablet_instances.html",
                tablet=instance.tablet,
                saved=saved,
                saved_instance_id=instance.id,
                **instance_table(instance.tablet_id, show_notes=show_notes),
            )
        )
    else:
        response = redirect(
            url_for(
                "cdpp.tablet",
                tablet_id=instance.tablet_id,
                notes=None if show_notes else "hide",
                _anchor=f"instance-{instance.id}",
            ),
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


def instance_form(
    instance: Instance,
    *,
    values: Mapping[str, str],
    author: str,
    comment: str,
    show_notes: bool,
    columns: int,
    inline: bool,
    errors: Mapping[str, str] | None = None,
    conflict: bool = False,
    status: int = 200,
) -> ResponseReturnValue:
    """Render the edit form, in a table row for htmx or on a page of its own.

    htmx swaps only successful responses, so a row for htmx has the status
    200, and headers that replace the row instead of the table.
    """
    context = {
        "instance": instance,
        "values": values,
        "author": author,
        "comment": comment,
        "seen": fingerprint(instance, INSTANCE_FIELDS),
        "errors": errors or {},
        "conflict": conflict,
        "options": lookup_options(),
        "show_notes": show_notes,
        "columns": columns,
        "inline": inline,
    }
    if inline:
        response = make_response(render_template("_instance_form_row.html", **context))
        if request.method == "POST":
            response.headers["HX-Retarget"] = f"#instance-{instance.id}"
            response.headers["HX-Reswap"] = "outerHTML"
    else:
        response = make_response(render_template("instance_edit.html", **context))
        response.status_code = status
    response.vary.update(("HX-Request", "HX-Target"))
    return response
