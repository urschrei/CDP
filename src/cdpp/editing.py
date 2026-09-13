"""Edits of records, with a change set for each save.

``save`` changes a record and records the old and new values in the same
transaction. ``revert`` undoes a change set with a new change set. Change sets
are never changed or deleted.
"""

import hashlib
import json
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select

from cdpp.db import Base, db
from cdpp.models import Change, ChangeSet, Entity


class EditConflict(Exception):
    """The record changed after the editor loaded it."""


class RevertConflict(Exception):
    """A later change set changed values that the change set to undo sets."""

    def __init__(self, changes: Sequence[Change]) -> None:
        super().__init__(f"{len(changes)} values changed after the change set")
        self.changes = list(changes)


def utc_now() -> datetime:
    """Return the time in UTC, without a time zone, as the database stores it."""
    return datetime.now(UTC).replace(tzinfo=None)


def fingerprint(record: Entity, fields: Sequence[str]) -> str:
    """Return a digest of the values of ``fields`` on ``record``.

    An edit form sends the digest back. If the digest is different when the
    form is saved, someone changed the record after the form was loaded. The
    order of ``fields`` does not change the digest.
    """
    values = json.dumps(
        {field: getattr(record, field) for field in fields}, sort_keys=True
    )
    return hashlib.sha256(values.encode()).hexdigest()


def save(
    record: Entity,
    values: Mapping[str, Any],
    *,
    author: str,
    seen: str,
    comment: str | None = None,
) -> ChangeSet | None:
    """Set ``values`` on ``record``, record a change set, and commit.

    ``seen`` is the fingerprint of the fields of ``values`` when the editor
    loaded the record.

    If no value changes, commit nothing and return None. If the record changed
    after the editor loaded it, commit nothing and raise EditConflict.
    """
    if fingerprint(record, list(values)) != seen:
        db.session.rollback()
        raise EditConflict
    changed = {
        field: value
        for field, value in values.items()
        if getattr(record, field) != value
    }
    if not changed:
        db.session.rollback()
        return None

    change_set = ChangeSet(author=author, created_at=utc_now(), comment=comment)
    for field, value in changed.items():
        change_set.changes.append(
            Change(
                kind="update",
                table_name=type(record).__tablename__,
                record_id=record.id,
                field=field,
                old_value=getattr(record, field),
                new_value=value,
            )
        )
        setattr(record, field, value)
    db.session.add(change_set)
    db.session.commit()
    return change_set


def revert(
    change_set: ChangeSet, *, author: str, comment: str | None = None
) -> ChangeSet:
    """Undo ``change_set`` with a new change set, and commit.

    If a later change set changed a value that ``change_set`` set, commit
    nothing and raise RevertConflict.
    """
    updates = db.session.scalars(
        select(Change)
        .where(Change.change_set_id == change_set.id, Change.kind == "update")
        .order_by(Change.id)
    ).all()
    if not updates:
        raise ValueError(f"Change set {change_set.id} changes no values.")

    records: dict[tuple[str, int], Entity] = {}
    for change in updates:
        key = (change.table_name, change.record_id)
        if key not in records:
            model = model_for(change.table_name)
            records[key] = db.session.get_one(model, change.record_id)
    stale = [
        change
        for change in updates
        if getattr(records[(change.table_name, change.record_id)], change.field)
        != change.new_value
    ]
    if stale:
        raise RevertConflict(stale)

    reverting = ChangeSet(
        author=author,
        created_at=utc_now(),
        comment=comment,
        reverts_id=change_set.id,
    )
    for change in updates:
        reverting.changes.append(
            Change(
                kind="update",
                table_name=change.table_name,
                record_id=change.record_id,
                field=change.field,
                old_value=change.new_value,
                new_value=change.old_value,
            )
        )
        record = records[(change.table_name, change.record_id)]
        setattr(record, change.field, change.old_value)
    db.session.add(reverting)
    db.session.commit()
    return reverting


def model_for(table_name: str) -> type[Entity]:
    """Return the model of the table ``table_name``."""
    for mapper in Base.registry.mappers:
        model = mapper.class_
        if issubclass(model, Entity) and model.__tablename__ == table_name:
            return model
    raise LookupError(f"No model has the table {table_name}.")
