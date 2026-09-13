import pytest
from flask.testing import FlaskClient
from sqlalchemy import func, select

from cdpp.db import db
from cdpp.editing import fingerprint, save
from cdpp.editor import (
    EDITOR_COOKIE,
    INSTANCE_FIELDS,
    column_number,
    current_values,
    iteration_number,
    line_number,
)
from cdpp.models import Change, ChangeSet, Instance, Line
from tests.conftest import Sample


def instance_id() -> int:
    statement = select(Instance.id).where(Instance.filename == "I_1")
    return db.session.scalars(statement).one()


def form_data(**changes: str) -> dict[str, str]:
    """Return a complete form for the first instance, with ``changes``."""
    instance = db.session.get_one(Instance, instance_id())
    data = current_values(instance) | {
        "author": "JJT",
        "comment": "",
        "seen": fingerprint(instance, INSTANCE_FIELDS),
    }
    db.session.expunge_all()
    return data | changes


def htmx(target: str) -> dict[str, str]:
    return {"HX-Request": "true", "HX-Target": target}


def change_set_count() -> int | None:
    return db.session.scalar(select(func.count()).select_from(ChangeSet))


def saved_line() -> str | None:
    db.session.expire_all()
    instance = db.session.get_one(Instance, instance_id())
    return instance.line.number if instance.line else None


def test_tablet_page_links_each_sign_to_its_edit_form(
    client: FlaskClient, sample: Sample
) -> None:
    html = client.get(f"/tablets/{sample.tablet.id}").get_data(as_text=True)

    assert f'<tr id="instance-{instance_id()}"' in html
    assert f'hx-get="/instances/{instance_id()}/edit?columns=' in html


def test_edit_page_shows_the_current_values_and_the_editor_name(
    client: FlaskClient, sample: Sample
) -> None:
    client.set_cookie(EDITOR_COOKIE, "JJT")

    html = client.get(f"/instances/{instance_id()}/edit").get_data(as_text=True)

    assert '<html lang="en-GB">' in html
    assert 'name="line" type="text" value="1"' in html
    assert 'name="author" type="text" value="JJT"' in html


def test_edit_form_for_htmx_is_a_table_row(client: FlaskClient, sample: Sample) -> None:
    url = f"/instances/{instance_id()}/edit?columns=5"

    html = client.get(url, headers=htmx(f"instance-{instance_id()}")).get_data(
        as_text=True
    )

    assert "<html" not in html
    assert f'<tr id="instance-{instance_id()}"' in html
    assert 'colspan="5"' in html


def test_save_changes_the_instance_and_records_a_change_set(
    client: FlaskClient, sample: Sample
) -> None:
    data = form_data(line="3′", comment="Read from the photograph")

    response = client.post(f"/instances/{instance_id()}/edit", data=data)

    assert response.status_code == 303
    assert response.location.endswith(
        f"/tablets/{sample.tablet.id}#instance-{instance_id()}"
    )
    assert f"{EDITOR_COOKIE}=JJT" in response.headers["Set-Cookie"]
    assert saved_line() == "03'"
    change_set = db.session.scalars(select(ChangeSet)).one()
    assert (change_set.author, change_set.comment) == (
        "JJT",
        "Read from the photograph",
    )
    kinds = db.session.scalars(select(Change.kind).order_by(Change.id)).all()
    assert kinds == ["insert", "update"]


def test_save_for_htmx_returns_the_table_with_the_new_value(
    client: FlaskClient, sample: Sample
) -> None:
    data = form_data(line="3′")

    response = client.post(
        f"/instances/{instance_id()}/edit", data=data, headers=htmx("tablet-instances")
    )

    html = response.get_data(as_text=True)
    assert response.status_code == 200
    assert 'id="tablet-instances"' in html
    assert "Saved the change to this instance of AŠ." in html
    assert ">3′</td>" in html


def test_save_without_a_name_is_refused(client: FlaskClient, sample: Sample) -> None:
    response = client.post(
        f"/instances/{instance_id()}/edit", data=form_data(line="4", author=" ")
    )

    assert response.status_code == 422
    assert "Enter your name." in response.get_data(as_text=True)
    assert saved_line() == "1"
    assert change_set_count() == 0


def test_save_with_an_invalid_line_is_refused_without_new_lines(
    client: FlaskClient, sample: Sample
) -> None:
    response = client.post(
        f"/instances/{instance_id()}/edit", data=form_data(line="3a", column="ii")
    )

    assert response.status_code == 422
    assert "Enter a line number" in response.get_data(as_text=True)
    assert db.session.scalars(select(func.count()).select_from(Line)).one() == 1


def test_invalid_save_for_htmx_replaces_the_form_row(
    client: FlaskClient, sample: Sample
) -> None:
    response = client.post(
        f"/instances/{instance_id()}/edit",
        data=form_data(line="3a"),
        headers=htmx("tablet-instances"),
    )

    assert response.status_code == 200
    assert response.headers["HX-Retarget"] == f"#instance-{instance_id()}"
    assert response.headers["HX-Reswap"] == "outerHTML"


def test_edit_form_says_that_it_changes_one_instance(
    client: FlaskClient, sample: Sample
) -> None:
    url = f"/instances/{instance_id()}/edit?columns=5"

    row = client.get(url, headers=htmx(f"instance-{instance_id()}"))
    page = client.get(url)

    for html in (row.get_data(as_text=True), page.get_data(as_text=True)):
        assert "This form changes only this instance of" in html
        assert "It does not change the sign or its other instances." in html
    assert 'alt="Photograph of this instance of AŠ on A.1"' in row.get_data(
        as_text=True
    )
    assert "<title>Edit an instance of AŠ on A.1" in page.get_data(as_text=True)


def test_save_after_another_save_shows_the_saved_values(
    client: FlaskClient, sample: Sample
) -> None:
    stale = form_data(line="5")
    instance = db.session.get_one(Instance, instance_id())
    save(
        instance,
        {"line_id": None},
        author="Another editor",
        seen=fingerprint(instance, ["line_id"]),
    )

    response = client.post(f"/instances/{instance_id()}/edit", data=stale)

    assert response.status_code == 409
    assert "Someone saved a change to this instance" in response.get_data(as_text=True)
    assert saved_line() is None
    assert change_set_count() == 1


def test_form_from_another_site_is_refused(client: FlaskClient, sample: Sample) -> None:
    response = client.post(
        f"/instances/{instance_id()}/edit",
        data=form_data(line="6"),
        headers={"Origin": "https://example.com"},
    )

    assert response.status_code == 403
    assert saved_line() == "1"


@pytest.mark.parametrize(
    ("parse", "text", "number"),
    [
        (line_number, "3′", "03'"),
        (line_number, " 12 '' ", "12''"),
        (line_number, "123", "123"),
        (column_number, "II′", "ii'"),
        (column_number, "iv", "iv"),
        (iteration_number, "2", "2"),
    ],
)
def test_numbers_are_written_as_the_data_write_them(parse, text, number) -> None:
    assert parse(text) == number


@pytest.mark.parametrize(
    ("parse", "text"),
    [
        (line_number, "3a"),
        (line_number, "1234"),
        (column_number, "2"),
        (column_number, "viii''"),
        (iteration_number, "0"),
    ],
)
def test_numbers_in_other_forms_are_refused(parse, text) -> None:
    with pytest.raises(ValueError):
        parse(text)
