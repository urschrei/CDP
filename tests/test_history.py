from flask.testing import FlaskClient
from sqlalchemy import select

from cdpp.db import db
from cdpp.editing import fingerprint, save
from cdpp.models import ChangeSet, Instance, Line
from tests.conftest import Sample


def first_instance() -> Instance:
    return db.session.scalars(select(Instance).where(Instance.filename == "I_1")).one()


def set_line(number: str | None, author: str = "JJT") -> int:
    """Set the line of the first instance, and return the ID of the change set."""
    instance = first_instance()
    seen = fingerprint(instance, ["line_id"])
    inserted = []
    line_id = None
    if number is not None:
        line = Line(number=number)
        db.session.add(line)
        db.session.flush()
        inserted, line_id = [line], line.id
    change_set = save(
        instance,
        {"line_id": line_id},
        author=author,
        seen=seen,
        comment="From the photograph",
        inserted=inserted,
    )
    assert change_set is not None
    change_set_id = change_set.id
    db.session.expunge_all()
    return change_set_id


def page(client: FlaskClient, url: str) -> str:
    response = client.get(url)
    assert response.status_code == 200
    return response.get_data(as_text=True)


def test_history_of_an_unedited_instance_says_so(
    client: FlaskClient, sample: Sample
) -> None:
    html = page(client, f"/instances/{first_instance().id}/history")

    assert "No one has edited this sign on this tablet." in html


def test_history_shows_each_change_with_its_old_and_new_value(
    client: FlaskClient, sample: Sample
) -> None:
    instance_id = first_instance().id
    change_set_id = set_line("03'")

    html = page(client, f"/instances/{instance_id}/history")

    assert f">Change set {change_set_id}</a>" in html
    assert "From the photograph" in html
    assert ">New line number</td>" in html
    assert ">Line</td>" in html
    assert ">1</td>" in html
    assert ">3′</td>" in html


def test_changes_page_lists_the_newest_change_set_first(
    client: FlaskClient, sample: Sample
) -> None:
    first = set_line("03'", author="First editor")
    second = set_line(None, author="Second editor")

    html = page(client, "/changes")

    assert html.index(f"Change set {second}") < html.index(f"Change set {first}")


def test_undo_sets_the_old_value_and_records_a_new_change_set(
    client: FlaskClient, sample: Sample
) -> None:
    change_set_id = set_line("03'")

    response = client.post(f"/changes/{change_set_id}/undo", data={"author": "JJT"})

    assert response.status_code == 303
    undo = db.session.scalars(
        select(ChangeSet).where(ChangeSet.reverts_id == change_set_id)
    ).one()
    assert response.location.endswith(f"/changes/{undo.id}?undone={change_set_id}")
    db.session.expire_all()
    line = first_instance().line
    assert line is not None
    assert line.number == "1"
    html = page(client, f"/changes/{change_set_id}")
    assert "Undone by" in html
    assert "Undo this change set" not in html


def test_undo_without_a_name_is_refused(client: FlaskClient, sample: Sample) -> None:
    change_set_id = set_line("03'")

    response = client.post(f"/changes/{change_set_id}/undo", data={"author": ""})

    assert response.status_code == 422
    assert "Enter your name." in response.get_data(as_text=True)
    reverting = select(ChangeSet).where(ChangeSet.reverts_id == change_set_id)
    assert db.session.scalars(reverting).first() is None


def test_undo_of_a_value_that_changed_later_is_refused(
    client: FlaskClient, sample: Sample
) -> None:
    change_set_id = set_line("03'")
    set_line(None, author="Later editor")

    response = client.post(f"/changes/{change_set_id}/undo", data={"author": "JJT"})

    assert response.status_code == 409
    assert "later change sets changed these values" in response.get_data(as_text=True)
    db.session.expire_all()
    assert first_instance().line is None


def test_undo_from_another_site_is_refused(client: FlaskClient, sample: Sample) -> None:
    change_set_id = set_line("03'")

    response = client.post(
        f"/changes/{change_set_id}/undo",
        data={"author": "JJT"},
        headers={"Origin": "https://example.com"},
    )

    assert response.status_code == 403


def test_edit_form_and_navigation_link_to_the_history(
    client: FlaskClient, sample: Sample
) -> None:
    instance_id = first_instance().id

    html = page(client, f"/instances/{instance_id}/edit")

    assert f'href="/instances/{instance_id}/history"' in html
    assert 'href="/changes"' in html
