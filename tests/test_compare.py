import struct
from pathlib import Path

from flask import Flask
from flask.testing import FlaskClient
from sqlalchemy import select

from cdpp.db import db
from cdpp.instances import COMPARISON_LIMIT, comparison_ids
from cdpp.models import Instance, Medium, Period, Tablet
from tests.conftest import Sample

GIF = b"GIF89a" + struct.pack("<HH", 30, 20) + b"\x00" * 10


def instance_ids() -> dict[str, int]:
    return dict(
        db.session.execute(select(Instance.filename, Instance.id)).tuples().all()
    )


def page(client: FlaskClient, url: str) -> str:
    response = client.get(url)
    assert response.status_code == 200
    return response.get_data(as_text=True)


def test_comparison_ids_omit_duplicates_and_values_that_are_not_ids() -> None:
    assert comparison_ids("3, 1,3,x,²,,-2") == [3, 1]
    assert comparison_ids(None) == []


def test_comparison_ids_stop_at_the_limit() -> None:
    text = ",".join(str(number) for number in range(1, 20))

    assert comparison_ids(text) == list(range(1, COMPARISON_LIMIT + 1))


def test_comparison_shows_the_instances_in_order_at_one_scale(
    app: Flask, client: FlaskClient, sample: Sample
) -> None:
    (Path(app.config["MEDIA_ROOT"]) / "instance" / "I_1.jpg").write_bytes(GIF)
    first, second = instance_ids()["I_1"], instance_ids()["I_2"]

    html = page(client, f"/compare?instances={second},{first},{second},999&scale=4")

    assert "<title>Comparison of 2 instances" in html
    assert html.index("/media/instance/I_2.jpg") < html.index("/media/instance/I_1.jpg")
    assert 'width="120" height="80"' in html
    assert "Old Babylonian" in html
    assert f'href="/compare?instances={first}&amp;scale=4"' in html
    assert f'href="/instances/{second}?compare={second},{first}&amp;scale=4"' in html


def test_empty_comparison(client: FlaskClient) -> None:
    assert "No instances." in page(client, "/compare")


def test_instance_page_adds_the_instance_to_the_comparison(
    client: FlaskClient, sample: Sample
) -> None:
    first, second = instance_ids()["I_1"], instance_ids()["I_2"]

    html = page(client, f"/instances/{first}")

    assert f'href="/instances/{first}?compare={first}"' in html
    assert ">Add to comparison</a>" in html
    assert "/compare?" not in html

    html = page(client, f"/instances/{first}?compare={second}")

    assert f'href="/instances/{first}?compare={second},{first}"' in html
    assert f'href="/compare?instances={second}"' in html
    # The link to the neighbouring instance keeps the comparison.
    assert f'href="/instances/{second}?compare={second}" rel="prev"' in html


def test_instance_page_removes_the_instance_from_the_comparison(
    client: FlaskClient, sample: Sample
) -> None:
    first, second = instance_ids()["I_1"], instance_ids()["I_2"]

    html = page(client, f"/instances/{first}?compare={first},{second}")

    assert f'href="/instances/{first}?compare={second}"' in html
    assert ">Remove from comparison</a>" in html
    assert ">Compare 2 instances</a>" in html


def test_full_comparison_has_no_add_link(client: FlaskClient, sample: Sample) -> None:
    others = ",".join(str(1000 + number) for number in range(COMPARISON_LIMIT))

    html = page(client, f"/instances/{instance_ids()['I_1']}?compare={others}")

    assert "Add to comparison" not in html
    assert f"Compare {COMPARISON_LIMIT} instances" in html


def test_sign_page_compares_one_instance_from_each_period(
    client: FlaskClient, sample: Sample
) -> None:
    first = instance_ids()["I_1"]
    assert "Compare periods" not in page(client, f"/signs/{sample.sign.id}")
    db.session.add(
        Tablet(
            museum_number="B.2",
            medium=Medium(name="bone"),
            period=Period(name="Old Assyrian", from_date="2000 BC", to_date="1750 BC"),
            instances=[Instance(sign_id=sample.sign.id, filename="I_3")],
        )
    )
    db.session.commit()
    third = instance_ids()["I_3"]
    db.session.expunge_all()

    html = page(client, f"/signs/{sample.sign.id}")
    response = client.get(f"/compare?sign={sample.sign.id}")

    assert f'href="/compare?sign={sample.sign.id}">Compare periods</a>' in html
    assert response.status_code == 302
    # Old Assyrian begins in 2000 BC. The sample period has no year.
    assert response.location == f"/compare?instances={third},{first}"


def test_comparison_of_an_unknown_sign_is_not_found(client: FlaskClient) -> None:
    assert client.get("/compare?sign=999").status_code == 404
