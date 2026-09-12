from pathlib import Path

import pytest
from flask import Flask
from flask.testing import FlaskClient

from cdpp.search import EXTENSION_KEY, SearchIndex, SearchResults, SearchUnavailable
from tests.conftest import Sample


class FakeSearchIndex(SearchIndex):
    """Return fixed results, or raise SearchUnavailable if there are none."""

    def __init__(self, results: SearchResults | None) -> None:
        self.results = results

    def search(self, query: str, limit: int = 50) -> SearchResults:
        if self.results is None:
            raise SearchUnavailable("connection refused")
        return self.results


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


def test_search_shows_results_in_rank_order(
    app: Flask, client: FlaskClient, sample: Sample
) -> None:
    app.extensions[EXTENSION_KEY] = FakeSearchIndex(
        SearchResults(
            sign_ids=[sample.sign_without_records.id, sample.sign.id],
            tablet_ids=[sample.tablet.id],
            estimated_signs=2,
            estimated_tablets=1,
        )
    )

    html = page(client, "/search?q=a")

    assert html.index(">ZA</a>") < html.index(">AŠ</a>")
    assert ">A.1</a>" in html
    assert "2 signs and 1 tablet match" in html


def test_search_returns_only_the_results_to_htmx(
    app: Flask, client: FlaskClient, sample: Sample
) -> None:
    app.extensions[EXTENSION_KEY] = FakeSearchIndex(
        SearchResults(
            sign_ids=[], tablet_ids=[], estimated_signs=0, estimated_tablets=0
        )
    )

    html = page(client, "/search?q=xyz", **htmx("search-results"))

    assert "<html" not in html
    assert 'hx-swap-oob="innerHTML:#search-status"' in html
    assert "No signs or tablets match" in html


def test_search_reports_that_the_service_is_not_available(
    app: Flask, client: FlaskClient
) -> None:
    app.extensions[EXTENSION_KEY] = FakeSearchIndex(None)

    response = client.get("/search?q=a")

    assert response.status_code == 503
    assert "Search is not available" in response.get_data(as_text=True)


def test_instance_images_come_from_the_media_root(
    app: Flask, client: FlaskClient
) -> None:
    (Path(app.config["MEDIA_ROOT"]) / "instance" / "I_9.jpg").write_bytes(b"jpeg")

    assert client.get("/media/instance/I_9.jpg").data == b"jpeg"
    assert client.get("/media/instance/I_10.jpg").status_code == 404
