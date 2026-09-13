import pytest
from flask import Flask
from flask.testing import FlaskClient
from sqlalchemy import update

from cdpp.db import db
from cdpp.filters import filter_options
from cdpp.models import Tablet
from cdpp.publications import Publication, parse_publication
from tests.conftest import Sample


@pytest.mark.parametrize(
    ("text", "series", "citation"),
    [
        ("SAA 8, 70", "SAA", "SAA 8, no. 70"),
        ("BCT 2, S9", "BCT", "BCT 2, no. S9"),
        ("CT 48 no. 21", "CT", "CT 48, no. 21"),
        ("AAT 27", "AAT", "AAT 27"),
        ("MSL 14 p. 19: Bk", "MSL", "MSL 14, p. 19, Bk"),
        ("MSL 14 p. 19: Bo, 20: Co", "MSL", "MSL 14, p. 19: Bo, 20: Co"),
        ("MSL SS 1 p. 108", "MSL SS", "MSL SS 1, p. 108"),
        ("UF 10 (1978) 124 no. 5", "UF", "UF 10 (1978), p. 124, no. 5"),
        ("MVAG 35,3 (1935) pp. 105 f.", "MVAG", "MVAG 35,3 (1935), p. 105 f."),
        ("RIME.4.3.6.12", "RIME", "RIME 4, no. E4.3.6.12"),
        ("RIME.3/2.1.1.33", "RIME", "RIME 3/2, no. E3/2.1.1.33"),
        ("RIMA.0.76.1", "RIMA", "RIMA, no. A.0.76.1"),
        ("RIMA.1.0.60.1", "RIMA", "RIMA 1, no. A.0.60.1"),
        ("Jeyes (1989) no. 11", "Jeyes (1989)", "Jeyes (1989), no. 11"),
        ("Kraus (1984) p. 372 (14)", "Kraus (1984)", "Kraus (1984), p. 372, no. 14"),
        (
            "Bongenaar (1997) pp. 63-64",
            "Bongenaar (1997)",
            "Bongenaar (1997), pp. 63-64",
        ),
        ("Roth (1997) MAL B", "Roth (1997)", "Roth (1997) MAL B"),
        ("Smith (1949)", "Smith (1949)", "Smith (1949)"),
        (
            "King, BBS pp. 120-127, pls. XCVIII-CII",
            "King, BBS",
            "King, BBS, pp. 120-127, pls. XCVIII-CII",
        ),
        ("Larsen, OACT p. 90 f.", "Larsen, OACT", "Larsen, OACT, p. 90 f."),
        ("unpublished", None, "unpublished"),
    ],
)
def test_publications_have_a_series_and_one_form_of_citation(
    text: str, series: str | None, citation: str
) -> None:
    publication = parse_publication(text)

    assert publication.original == text
    assert publication.series == series
    assert publication.citation == citation


def test_parts_of_a_publication() -> None:
    assert parse_publication("UF 10 (1978) 124 no. 5") == Publication(
        "UF 10 (1978) 124 no. 5",
        series="UF",
        volume="10",
        year="1978",
        page="124",
        number="5",
    )
    assert parse_publication("MSL 14 p. 21: De") == Publication(
        "MSL 14 p. 21: De", series="MSL", volume="14", page="21", siglum="De"
    )


def set_publication(tablet_id: int, text: str) -> None:
    statement = update(Tablet).where(Tablet.id == tablet_id).values(publication=text)
    db.session.execute(statement)
    db.session.commit()


def test_tablet_pages_show_the_series_and_the_citation(
    client: FlaskClient, sample: Sample
) -> None:
    set_publication(sample.tablet.id, "SAA 8, 70")

    html = client.get(f"/tablets/{sample.tablet.id}").get_data(as_text=True)

    assert '<a href="/tablets?series=SAA">SAA</a>' in html
    assert "<dd>SAA 8, no. 70</dd>" in html


def test_the_tablet_list_filters_by_series(
    app: Flask, client: FlaskClient, sample: Sample
) -> None:
    set_publication(sample.tablet.id, "SAA 8, 70")
    set_publication(sample.tablet_without_instances.id, "MSL 14 p. 19: Bk")

    html = client.get("/tablets?series=MSL").get_data(as_text=True)

    assert f'href="/tablets/{sample.tablet_without_instances.id}"' in html
    assert f'href="/tablets/{sample.tablet.id}"' not in html
    options = {tablet_filter.key: names for tablet_filter, names in filter_options()}
    assert options["series"] == ["MSL", "SAA"]
