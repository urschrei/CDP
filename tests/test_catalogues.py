import csv
from pathlib import Path

import pytest
from flask import Flask
from flask.testing import FlaskClient
from sqlalchemy import select

from cdpp.catalogues import CDLI_FIELDS, catalogue_keys, match_cdli, tablet_key
from cdpp.db import db
from cdpp.models import CdliArtifact
from tests.conftest import Sample


def cdli_row(
    id_text: str,
    museum_no: str,
    accession_no: str = "",
    designation: str = "",
) -> dict[str, str]:
    return {
        "id_text": id_text,
        "designation": designation or museum_no,
        "museum_no": museum_no,
        "accession_no": accession_no,
        "primary_publication": "",
        "publication_history": "",
    }


@pytest.mark.parametrize(
    ("museum_number", "catalogue_value"),
    [
        ("BM_91082", "BM 091082 (was BM 012225)"),
        ("81_2-4_287", "1881-02-04, 0287"),
        ("91_5-9_3", "1891-05-09 Bu, 0003"),
        ("A_8992", "OIM A08992"),
        ("1923_339", "Ashm 1923-0339"),
        ("L_29-580", "UM L-29-580 & UM L-29-585 + UM L-29-630"),
        ("VA_Ass_3221_c", "VA Ass 03221c"),
        ("Rm2_427", "Rm 2, 427"),
        ("K_39", "K 00039 + K 00153"),
        ("BM_14030_seal", "BM 014030"),
        ("UM_29_15_513", "UM 29-15-513"),
    ],
)
def test_museum_numbers_match_their_catalogue_forms(
    museum_number: str, catalogue_value: str
) -> None:
    assert tablet_key(museum_number) in catalogue_keys(catalogue_value)


@pytest.mark.parametrize(
    ("museum_number", "catalogue_value"),
    [
        ("K_39", "USC 6594"),
        ("K_39", "BM —"),
        ("BM_91082", "BM 091083"),
        ("Rm2_427", "Rm 24, 27"),
    ],
)
def test_other_museum_numbers_do_not_match(
    museum_number: str, catalogue_value: str
) -> None:
    assert tablet_key(museum_number) not in catalogue_keys(catalogue_value)


def test_match_prefers_the_object_then_a_join_then_an_accession_number() -> None:
    tablets = {1: "K_39", 2: "BM_80128_seal", 3: "81_2-4_287", 4: "K_15272"}
    rows = [
        cdli_row("235406", "USC 6594", "K039"),
        cdli_row("365272", "BM —", "K 00039 + K 00153"),
        cdli_row("366216", "BM 080127 & BM 080128"),
        cdli_row("366217", "BM 080128"),
        cdli_row("1", "BM —", "1881-02-04, 0287"),
        cdli_row("336039", "BM 134596 +", "K 15272 + Rm 0120"),
    ]

    matches = match_cdli(rows, tablets)

    assert {
        tablet_id: [row["id_text"] for row in matched]
        for tablet_id, matched in matches.items()
    } == {1: ["365272"], 2: ["366217"], 3: ["1"], 4: ["336039"]}


def test_import_cdli_replaces_the_snapshot_and_links_tablet_pages(
    app: Flask, client: FlaskClient, sample: Sample, tmp_path: Path
) -> None:
    catalogue = tmp_path / "cdli_cat.csv"
    with catalogue.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=CDLI_FIELDS)
        writer.writeheader()
        writer.writerow(cdli_row("12345", "BM 012345"))
        writer.writerow(cdli_row("7", "OIM A 1"))
        writer.writerow(cdli_row("8", "USC 1", "A 1"))
    runner = app.test_cli_runner()

    for _ in range(2):
        result = runner.invoke(args=["import-cdli", str(catalogue)])
        assert result.exit_code == 0, result.output

    assert "Matched 2 tablets to 2 CDLI catalogue entries." in result.output
    stored = select(CdliArtifact.p_number).order_by(CdliArtifact.p_number)
    assert db.session.scalars(stored).all() == ["P000007", "P012345"]
    html = client.get(f"/tablets/{sample.tablet.id}").get_data(as_text=True)
    assert '<a href="https://cdli.earth/P000007">P000007</a>' in html
