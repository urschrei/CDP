from typing import Any

import pytest
from sqlalchemy import func, select

from cdpp.db import db
from cdpp.editing import EditConflict, RevertConflict, fingerprint, revert, save
from cdpp.models import Change, ChangeSet, Instance
from tests.conftest import Sample


def first_instance() -> Instance:
    return db.session.scalars(select(Instance).where(Instance.filename == "I_1")).one()


def recorded_changes() -> list[tuple[Any, ...]]:
    statement = select(
        Change.kind, Change.table_name, Change.field, Change.old_value, Change.new_value
    ).order_by(Change.id)
    return [tuple(row) for row in db.session.execute(statement)]


def change_set_count() -> int | None:
    return db.session.scalar(select(func.count()).select_from(ChangeSet))


def set_line(instance: Instance, line: str | None, author: str) -> ChangeSet | None:
    return save(
        instance,
        {"line": line},
        author=author,
        seen=fingerprint(instance, ["line"]),
    )


def test_fingerprint_does_not_depend_on_the_order_of_the_fields(
    sample: Sample,
) -> None:
    instance = first_instance()

    assert fingerprint(instance, ["line", "surface_id"]) == fingerprint(
        instance, ["surface_id", "line"]
    )


def test_save_changes_the_record_and_records_the_change_set(sample: Sample) -> None:
    instance = first_instance()
    seen = fingerprint(instance, ["line"])

    change_set = save(
        instance,
        {"line": "02"},
        author="JJT",
        seen=seen,
        comment="Checked against the photograph",
    )

    assert change_set is not None
    assert first_instance().line == "02"
    stored = db.session.get_one(ChangeSet, change_set.id)
    assert (stored.author, stored.comment, stored.reverts_id) == (
        "JJT",
        "Checked against the photograph",
        None,
    )
    assert recorded_changes() == [("update", "instance", "line", "1", "02")]


def test_save_without_a_changed_value_records_nothing(sample: Sample) -> None:
    instance = first_instance()

    assert set_line(instance, instance.line, author="JJT") is None
    assert change_set_count() == 0


def test_save_refuses_a_record_that_changed_after_it_was_loaded(
    sample: Sample,
) -> None:
    instance = first_instance()
    seen_by_second_editor = fingerprint(instance, ["line"])
    set_line(instance, None, author="First editor")

    with pytest.raises(EditConflict):
        save(
            first_instance(),
            {"line": "03"},
            author="Second editor",
            seen=seen_by_second_editor,
        )

    assert first_instance().line is None
    assert change_set_count() == 1


def test_revert_sets_the_old_values_with_a_new_change_set(sample: Sample) -> None:
    original = set_line(first_instance(), None, author="First editor")
    assert original is not None

    undo = revert(original, author="Second editor", comment="The line was right")

    assert first_instance().line == "1"
    stored = db.session.get_one(ChangeSet, undo.id)
    assert (stored.reverts_id, stored.author) == (original.id, "Second editor")
    assert recorded_changes()[-1] == ("update", "instance", "line", None, "1")


def test_revert_refuses_a_value_that_a_later_change_set_changed(
    sample: Sample,
) -> None:
    original = set_line(first_instance(), None, author="First editor")
    assert original is not None
    set_line(first_instance(), "03", author="Second editor")

    with pytest.raises(RevertConflict) as raised:
        revert(original, author="Third editor")

    assert [change.field for change in raised.value.changes] == ["line"]
    assert first_instance().line == "03"
    assert change_set_count() == 2


def test_revert_of_a_revert_is_refused_after_the_values_change_back(
    sample: Sample,
) -> None:
    original = set_line(first_instance(), None, author="First editor")
    assert original is not None
    revert(original, author="Second editor")

    with pytest.raises(RevertConflict):
        revert(original, author="Third editor")
