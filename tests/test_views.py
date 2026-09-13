from pathlib import Path

import pytest
from flask import Flask
from flask.testing import FlaskClient
from sqlalchemy import update

from cdpp.db import db
from cdpp.models import Instance, Line, OraccListNumber, OraccSign, SignList, Surface
from cdpp.search import SearchResults
from cdpp.views import instance_location, position_text, search_status
from tests.conftest import Sample


def page(client: FlaskClient, url: str, **headers: str) -> str:
    response = client.get(url, headers=headers)
    assert response.status_code == 200
    return response.get_data(as_text=True)


def htmx(target: str) -> dict[str, str]:
    return {"HX-Request": "true", "HX-Target": target}


def test_home_page_shows_only_specimens_with_image_files(
    app: Flask, client: FlaskClient, sample: Sample
) -> None:
    (Path(app.config["MEDIA_ROOT"]) / "instance" / "I_1.jpg").write_bytes(b"jpeg")

    html = page(client, "/")

    assert "/media/instance/I_1.jpg" in html
    assert "/media/instance/I_2.jpg" not in html


def test_home_page_returns_only_the_specimens_to_htmx(
    client: FlaskClient, sample: Sample
) -> None:
    response = client.get("/", headers=htmx("specimens"))

    html = response.get_data(as_text=True)
    assert 'id="specimens"' in html
    assert "<html" not in html
    assert "HX-Target" in response.headers["Vary"]


def test_signs_page_counts_photographs(client: FlaskClient, sample: Sample) -> None:
    html = page(client, "/signs")

    assert ">AŠ</a>" in html
    assert ">ZA</a>" in html
    assert "2 photographs" in html


def test_signs_page_can_omit_signs_without_photographs(
    client: FlaskClient, sample: Sample
) -> None:
    html = page(client, "/signs?with_images=1")

    assert ">AŠ</a>" in html
    assert ">ZA</a>" not in html


def test_sign_page_omits_empty_sign_list_columns(
    client: FlaskClient, sample: Sample
) -> None:
    html = page(client, f"/signs/{sample.sign.id}")

    assert ">MesZL</th>" in html
    assert ">LAK</th>" in html
    assert "ZATU" not in html
    assert "horizontal wedge" in html


def test_sign_page_without_records_or_photographs(
    client: FlaskClient, sample: Sample
) -> None:
    html = page(client, f"/signs/{sample.sign_without_records.id}")

    assert "no sign-list entries" in html
    assert "no photographs" in html


def test_unknown_sign_is_not_found(client: FlaskClient, sample: Sample) -> None:
    response = client.get("/signs/999")

    assert response.status_code == 404
    assert "Page not found" in response.get_data(as_text=True)


def test_sign_images_are_grouped_by_tablet(client: FlaskClient, sample: Sample) -> None:
    html = page(client, f"/signs/{sample.sign.id}/images")

    assert f'id="tablet-{sample.tablet.id}"' in html
    assert "Obverse, line 1" in html
    assert "2 photographs on 1 tablet" in html


def test_tablet_page_links_details_to_filtered_lists(
    client: FlaskClient, sample: Sample
) -> None:
    html = page(client, f"/tablets/{sample.tablet.id}")

    assert 'href="/tablets?ruler=Zimri-Lim"' in html
    assert 'href="/tablets?sent_from=Zimri-Lim"' in html
    assert 'href="/tablets?city=Mari"' in html
    assert "Akkadian" in html
    assert "2 photographs of 1 sign" in html


def test_tablet_page_without_instances(client: FlaskClient, sample: Sample) -> None:
    html = page(client, f"/tablets/{sample.tablet_without_instances.id}")

    assert "no photographs of signs" in html


def test_tablet_images_are_grouped_by_sign(client: FlaskClient, sample: Sample) -> None:
    html = page(client, f"/tablets/{sample.tablet.id}/images")

    assert f'id="sign-{sample.sign.id}"' in html
    assert "Line 1" in html


@pytest.mark.parametrize(
    ("query", "included", "excluded"),
    [
        ("ruler=Zimri-Lim", "A.1", "BM_12345"),
        ("medium=stone", "BM_12345", "A.1"),
        ("sent_from=Zimri-Lim", "A.1", "BM_12345"),
        ("period=Old+Babylonian&medium=clay", "A.1", "BM_12345"),
    ],
)
def test_tablet_filters(
    client: FlaskClient, sample: Sample, query: str, included: str, excluded: str
) -> None:
    html = page(client, f"/tablets?{query}")

    assert f">{included}</a>" in html
    assert f">{excluded}</a>" not in html


def test_tablet_list_returns_only_the_results_to_htmx(
    client: FlaskClient, sample: Sample
) -> None:
    html = page(client, "/tablets?medium=stone", **htmx("tablet-results"))

    assert "<html" not in html
    assert 'hx-swap-oob="innerHTML:#tablet-status"' in html
    assert "Tablets 1 to 1 of 1." in html
    assert ">BM_12345</a>" in html


def test_search_shows_signs_and_tablets_in_rank_order(
    client: FlaskClient, sample: Sample
) -> None:
    html = page(client, "/search?q=a")

    # AŠ starts with the query; ZA only contains it.
    assert html.index(">AŠ</a>") < html.index(">ZA</a>")
    assert ">A.1</a>" in html
    assert "2 signs and 2 tablets match" in html


def test_search_returns_only_the_results_to_htmx(
    client: FlaskClient, sample: Sample
) -> None:
    html = page(client, "/search?q=xyz", **htmx("search-results"))

    assert "<html" not in html
    assert 'hx-swap-oob="innerHTML:#search-status"' in html
    assert "No signs or tablets match" in html


def test_instance_images_come_from_the_media_root(
    app: Flask, client: FlaskClient
) -> None:
    (Path(app.config["MEDIA_ROOT"]) / "instance" / "I_9.jpg").write_bytes(b"jpeg")

    assert client.get("/media/instance/I_9.jpg").data == b"jpeg"
    assert client.get("/media/instance/I_10.jpg").status_code == 404


def test_sign_page_links_numbers_and_names_to_the_oracc_sign_list(
    client: FlaskClient, sample: Sample
) -> None:
    for name, oracc_list in (("MesZL", "MZL"), ("LAK", "LAK")):
        db.session.execute(
            update(SignList).where(SignList.name == name).values(oracc_list=oracc_list)
        )
    db.session.add_all(
        [
            OraccSign(
                oid="o0000001",
                name="AŠ",
                ebl_url="https://www.ebl.lmu.de/signs/A%C5%A0",
                list_numbers=[OraccListNumber(list_name="MZL", number="001")],
            ),
            OraccSign(
                oid="o0000002",
                name="X",
                list_numbers=[OraccListNumber(list_name="LAK", number="002")],
            ),
            OraccSign(
                oid="o0000003",
                name="Y",
                list_numbers=[OraccListNumber(list_name="LAK", number="002")],
            ),
        ]
    )
    db.session.commit()

    html = page(client, f"/signs/{sample.sign.id}")

    # MesZL 1 is MZL001 of exactly one OSL sign, which is also named AŠ.
    assert '<a href="http://oracc.org/osl/signlist/o0000001">1<span' in html
    assert '<a href="http://oracc.org/osl/signlist/o0000001">AŠ<span' in html
    assert 'href="https://www.ebl.lmu.de/signs/A%C5%A0"' in html
    # LAK 2 is a number of two OSL signs, so it has no link.
    assert "o0000002" not in html
    assert "o0000003" not in html


def test_tablet_page_marks_default_positions(
    client: FlaskClient, sample: Sample
) -> None:
    html = page(client, f"/tablets/{sample.tablet.id}")

    # One instance has a surface, so the other instance shows the default.
    assert '>obv<span class="sr-only"> (default)</span>' in html
    assert "Values in italics are defaults" in html
    # No instance has a column or an iteration, so the table omits both.
    assert ">Column</th>" not in html
    assert ">Iteration</th>" not in html


@pytest.mark.parametrize(
    ("number", "text"),
    [("01'", "1′"), ("ii''", "ii′′"), ("10", "10"), ("0", "0"), ("003", "3")],
)
def test_position_text_removes_leading_zeros_and_shows_primes(
    number: str, text: str
) -> None:
    assert position_text(number) == text


def test_instance_location_shows_the_line_as_pages_show_it() -> None:
    instance = Instance(surface=Surface(name="rev"), line=Line(number="03'"))

    assert instance_location(instance) == "Rev, line 3′"


def test_tablet_page_can_hide_the_jjt_notes(
    client: FlaskClient, sample: Sample
) -> None:
    db.session.execute(
        update(Instance)
        .where(Instance.filename == "I_1")
        .values(jjt_notes="lang autoset to akk")
    )
    db.session.commit()
    url = f"/tablets/{sample.tablet.id}"

    shown = page(client, url)
    hidden = page(client, f"{url}?notes=hide")
    partial = page(client, f"{url}?notes=hide", **htmx("tablet-instances"))

    assert ">JJT notes (2012)</th>" in shown
    assert "lang autoset to akk" in shown
    assert f'href="{url}?notes=hide"' in shown
    assert ">JJT notes (2012)</th>" not in hidden
    assert "lang autoset to akk" not in hidden
    assert "Show JJT notes (1)" in hidden
    assert "<html" not in partial
    assert 'id="tablet-instances"' in partial
    assert "Show JJT notes (1)" in partial


def test_tablet_page_without_jjt_notes_has_no_notes_link(
    client: FlaskClient, sample: Sample
) -> None:
    html = page(client, f"/tablets/{sample.tablet.id}")

    assert "JJT notes" not in html


def test_search_status_omits_record_types_without_matches() -> None:
    results = SearchResults(sign_ids=[], tablet_ids=[7], sign_count=0, tablet_count=1)

    assert search_status("K_39", results) == "1 tablet matches “K_39”."
