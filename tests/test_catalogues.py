import csv
import json
import zipfile
from collections.abc import Iterable
from pathlib import Path

import pytest
from flask import Flask
from flask.testing import FlaskClient
from sqlalchemy import select

from cdpp.catalogues import (
    CDLI_FIELDS,
    catalogue_keys,
    match_cdli,
    match_oracc,
    read_oracc_archive,
    tablet_key,
)
from cdpp.db import db
from cdpp.models import CdliArtifact, OraccText
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
        "period": "",
        "provenience": "",
        "object_type": "",
        "material": "",
        "language": "",
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
        writer.writerow(
            {**cdli_row("7", "OIM A 1"), "period": "Old Babylonian (ca. 1900-1600 BC)"}
        )
        writer.writerow(cdli_row("8", "USC 1", "A 1"))
    runner = app.test_cli_runner()

    for _ in range(2):
        result = runner.invoke(args=["import-cdli", str(catalogue)])
        assert result.exit_code == 0, result.output

    assert "Matched 2 tablets to 2 CDLI catalogue entries." in result.output
    stored = select(CdliArtifact.p_number, CdliArtifact.period).order_by(
        CdliArtifact.p_number
    )
    assert db.session.execute(stored).tuples().all() == [
        ("P000007", "Old Babylonian (ca. 1900-1600 BC)"),
        ("P012345", None),
    ]
    html = client.get(f"/tablets/{sample.tablet.id}").get_data(as_text=True)
    assert '<a href="https://cdli.earth/P000007">P000007</a>' in html


def oracc_archive(
    path: Path, name: str, members: dict[str, dict[str, str]], edited: Iterable[str]
) -> Path:
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr(f"{name}/catalogue.json", json.dumps({"members": members}))
        for text_id in edited:
            archive.writestr(f"{name}/corpusjson/{text_id}.json", "{}")
    return path


def test_oracc_match_uses_numbers_and_exemplars_of_texts_with_pages(
    tmp_path: Path,
) -> None:
    path = oracc_archive(
        tmp_path / "saao.zip",
        "saao",
        {
            "P000001": {"project": "saao", "museum_no": "BM 012345"},
            "P000002": {"project": "saao", "museum_no": "BM 012345"},
            "P000003": {"project": "saa08", "accession_no": "K 00039 + K 00153"},
            "P000004": {"project": "saa08", "accession_no": "K 05422B"},
            "Q000005": {
                "project": "saao/saa02",
                "exemplars": "VAT 01000; Rm 2, 427 (+) K 00001",
            },
        },
        edited=["P000001"],
    )
    with path.open("rb") as file:
        archive = read_oracc_archive(file)
    tablets = {1: "BM_12345", 2: "K_39", 3: "Rm2_427", 4: "K_5422_a"}

    matches = match_oracc(archive, tablets)

    assert matches == {
        1: {("saao", "P000001")},
        2: {("saao/saa08", "P000003")},
        3: {("saao/saa02", "Q000005")},
    }


def test_import_oracc_texts_replaces_the_snapshot_and_links_tablet_pages(
    app: Flask, client: FlaskClient, sample: Sample, tmp_path: Path
) -> None:
    path = oracc_archive(
        tmp_path / "dcclt.zip",
        "dcclt",
        {
            "Q000001": {"project": "dcclt/nineveh", "exemplars": "A 1"},
            "P000002": {"project": "dcclt", "museum_no": "A 1"},
        },
        edited=[],
    )
    runner = app.test_cli_runner()

    for _ in range(2):
        result = runner.invoke(args=["import-oracc-texts", str(path)])
        assert result.exit_code == 0, result.output

    assert "Matched 1 tablets to 1 Oracc texts." in result.output
    assert db.session.scalars(select(OraccText.project)).all() == ["dcclt/nineveh"]
    html = client.get(f"/tablets/{sample.tablet.id}").get_data(as_text=True)
    assert '<dt class="text-muted">DCCLT</dt>' in html
    link = "https://oracc.museum.upenn.edu/dcclt/nineveh/Q000001"
    assert f'<a href="{link}">Q000001</a>' in html
