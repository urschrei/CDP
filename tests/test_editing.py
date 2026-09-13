from typing import Any

import pytest
from sqlalchemy import func, select

from cdpp.db import db
from cdpp.editing import EditConflict, RevertConflict, fingerprint, revert, save
from cdpp.models import Change, ChangeSet, Instance, Line
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


def new_line(number: str) -> Line:
    line = Line(number=number)
    db.session.add(line)
    db.session.flush()
    return line


def set_line(instance: Instance, line_id: int | None, author: str) -> ChangeSet | None:
    return save(
        instance,
        {"line_id": line_id},
        author=author,
        seen=fingerprint(instance, ["line_id"]),
    )


def test_save_changes_the_record_and_records_the_change_set(sample: Sample) -> None:
    instance = first_instance()
    old_line = instance.line_id
    seen = fingerprint(instance, ["line_id"])
    line = new_line("02")

    change_set = save(
        instance,
        {"line_id": line.id},
        author="JJT",
        seen=seen,
        comment="Checked against the photograph",
        inserted=[line],
    )

    assert change_set is not None
    assert first_instance().line_id == line.id
    stored = db.session.get_one(ChangeSet, change_set.id)
    assert (stored.author, stored.comment, stored.reverts_id) == (
        "JJT",
        "Checked against the photograph",
        None,
    )
    assert recorded_changes() == [
        ("insert", "line", "number", None, "02"),
        ("update", "instance", "line_id", old_line, line.id),
    ]


def test_save_without_a_changed_value_records_nothing(sample: Sample) -> None:
    instance = first_instance()

    assert set_line(instance, instance.line_id, author="JJT") is None
    assert change_set_count() == 0


def test_save_refuses_a_record_that_changed_after_it_was_loaded(
    sample: Sample,
) -> None:
    instance = first_instance()
    seen_by_second_editor = fingerprint(instance, ["line_id"])
    set_line(instance, None, author="First editor")
    line = new_line("03")

    with pytest.raises(EditConflict):
        save(
            first_instance(),
            {"line_id": line.id},
            author="Second editor",
            seen=seen_by_second_editor,
            inserted=[line],
        )

    assert first_instance().line_id is None
    assert change_set_count() == 1
    assert db.session.scalar(select(Line).where(Line.number == "03")) is None


def test_revert_sets_the_old_values_with_a_new_change_set(sample: Sample) -> None:
    instance = first_instance()
    old_line = instance.line_id
    original = set_line(instance, None, author="First editor")
    assert original is not None

    undo = revert(original, author="Second editor", comment="The line was right")

    assert first_instance().line_id == old_line
    stored = db.session.get_one(ChangeSet, undo.id)
    assert (stored.reverts_id, stored.author) == (original.id, "Second editor")
    assert recorded_changes()[-1] == ("update", "instance", "line_id", None, old_line)


def test_revert_refuses_a_value_that_a_later_change_set_changed(
    sample: Sample,
) -> None:
    original = set_line(first_instance(), None, author="First editor")
    assert original is not None
    line = new_line("03")
    set_line(first_instance(), line.id, author="Second editor")

    with pytest.raises(RevertConflict) as raised:
        revert(original, author="Third editor")

    assert [change.field for change in raised.value.changes] == ["line_id"]
    assert first_instance().line_id == line.id
    assert change_set_count() == 2


def test_revert_of_a_revert_is_refused_after_the_values_change_back(
    sample: Sample,
) -> None:
    original = set_line(first_instance(), None, author="First editor")
    assert original is not None
    revert(original, author="Second editor")

    with pytest.raises(RevertConflict):
        revert(original, author="Third editor")
