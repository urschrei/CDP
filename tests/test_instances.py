import struct
from pathlib import Path

import pytest
from flask import Flask
from flask.testing import FlaskClient
from sqlalchemy import select

from cdpp.db import db
from cdpp.editing import fingerprint, save
from cdpp.instances import period_start, position_key, roman_number
from cdpp.models import Instance, Period, Surface
from tests.conftest import Sample

PNG = b"\x89PNG\r\n\x1a\n" + b"\x00\x00\x00\rIHDR" + struct.pack(">II", 30, 20)


def instance_ids() -> dict[str, int]:
    return dict(
        db.session.execute(select(Instance.filename, Instance.id)).tuples().all()
    )


def page(client: FlaskClient, url: str) -> str:
    response = client.get(url)
    assert response.status_code == 200
    return response.get_data(as_text=True)


def test_instance_page_shows_the_photograph_at_twice_its_size(
    app: Flask, client: FlaskClient, sample: Sample
) -> None:
    (Path(app.config["MEDIA_ROOT"]) / "instance" / "I_1.png").write_bytes(PNG)
    url = f"/instances/{instance_ids()['I_1']}"

    html = page(client, url)

    assert "<title>Instance of AŠ on A.1" in html
    assert 'width="60" height="40"' in html
    assert "I_1, 30 × 20 px" in html
    assert 'aria-current="true">2×</a>' in html
    assert 'width="120" height="80"' in page(client, f"{url}?scale=4")
    assert 'width="60" height="40"' in page(client, f"{url}?scale=3")


def test_instance_page_shows_the_position_and_the_tablet(
    client: FlaskClient, sample: Sample
) -> None:
    html = page(client, f"/instances/{instance_ids()['I_2']}")

    assert '>obv<span class="sr-only"> (default)</span>' in html
    assert 'href="/tablets?city=Mari"' in html
    assert 'href="/tablets?ruler=Zimri-Lim"' in html
    assert f'href="/tablets/{sample.tablet.id}"' in html


def test_instance_page_links_to_the_neighbouring_instances(
    client: FlaskClient, sample: Sample
) -> None:
    ids = instance_ids()

    html = page(client, f"/instances/{ids['I_1']}")

    # I_2 has the default surface, obv. It comes before I_1, on the surface
    # "obverse".
    assert f'href="/instances/{ids["I_2"]}" rel="prev"' in html
    assert 'rel="next"' not in html


def test_instance_page_shows_the_latest_change(
    client: FlaskClient, sample: Sample
) -> None:
    ids = instance_ids()
    instance = db.session.get_one(Instance, ids["I_1"])
    save(
        instance,
        {"line": None},
        author="JJT",
        seen=fingerprint(instance, ["line"]),
    )
    db.session.expunge_all()

    html = page(client, f"/instances/{ids['I_1']}")

    assert "Last changed by JJT" in html


def test_photographs_link_to_their_instance_pages(
    client: FlaskClient, sample: Sample
) -> None:
    ids = instance_ids()

    html = page(client, f"/signs/{sample.sign.id}")

    assert f'href="/instances/{ids["I_1"]}"' in html


def test_unknown_instance_is_not_found(client: FlaskClient, sample: Sample) -> None:
    assert client.get("/instances/999").status_code == 404


@pytest.mark.parametrize(
    ("text", "value"),
    [("i", 1), ("iv", 4), ("ii'", 2), ("ix", 9), ("xii", 12), ("", 0)],
)
def test_roman_number(text: str, value: int) -> None:
    assert roman_number(text) == value


@pytest.mark.parametrize(("start_year", "start"), [(-1799, -1799), (75, 75), (None, 0)])
def test_period_start(start_year: int | None, start: int) -> None:
    assert period_start(Period(name="Period", start_year=start_year)) == start


def test_positions_sort_by_surface_column_and_line() -> None:
    def instance(
        instance_id: int, surface: str | None, column: str | None, line: str | None
    ) -> Instance:
        return Instance(
            id=instance_id,
            surface=Surface(name=surface) if surface else None,
            column=column,
            line=line,
        )

    instances = [
        instance(1, "rev", "i", "02"),
        instance(2, "obv", "ii", "10"),
        instance(3, "obv", "ii", "09"),
        instance(4, "obv", "i", "30"),
        instance(5, "colophon", None, "01"),
    ]

    assert [item.id for item in sorted(instances, key=position_key)] == [4, 3, 2, 1, 5]
