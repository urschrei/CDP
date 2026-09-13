import pytest
from flask import Flask
from sqlalchemy import text, update

from cdpp.db import db
from cdpp.models import CdliArtifact, Eponym, EponymYear, OraccText, Sign, Tablet
from cdpp.search import (
    SIGN_TABLE,
    TABLET_TABLE,
    normalise,
    rebuild,
    search_records,
    sign_documents,
    tablet_documents,
)
from tests.conftest import Sample


def sign_refs(query: str, limit: int = 50) -> list[str]:
    ids = search_records(query, limit=limit).sign_ids
    return [sign.sign_ref for sign in (db.session.get_one(Sign, i) for i in ids)]


def add_signs(*sign_refs: str) -> None:
    db.session.add_all(Sign(sign_ref=sign_ref) for sign_ref in sign_refs)
    db.session.commit()


def add_catalogue_values(sample: Sample) -> None:
    """Give the sample tablet CDLI and Oracc entries, and a year with an eponym."""
    tablet_id = sample.tablet.id
    eponym = Eponym(name="Ashur-dan")
    db.session.add_all(
        [
            CdliArtifact(
                tablet_id=tablet_id,
                p_number="P000001",
                designation="A 1",
                museum_no="BM 000001",
                provenience="Mari (mod. Tell Hariri)",
            ),
            OraccText(tablet_id=tablet_id, project="saao", text_id="P000001"),
            OraccText(tablet_id=tablet_id, project="dcclt", text_id="Q000002"),
            eponym,
        ]
    )
    db.session.flush()
    # 1761 BC.
    db.session.add(EponymYear(year=-1760, eponym_id=eponym.id))
    db.session.execute(update(Tablet).where(Tablet.id == tablet_id).values(year=-1760))
    db.session.commit()


def test_sign_documents_include_names_from_other_sign_lists(sample: Sample) -> None:
    documents = sign_documents()

    assert {
        "id": sample.sign.id,
        "sign_ref": "AŠ",
        "names": ["horizontal wedge"],
    } in documents
    assert {
        "id": sample.sign_without_records.id,
        "sign_ref": "ZA",
        "names": [],
    } in documents


def test_tablet_documents_name_the_related_records(sample: Sample) -> None:
    documents = {doc["id"]: doc for doc in tablet_documents()}

    document = documents[sample.tablet.id]
    assert document["museum_number"] == "A.1"
    assert document["rulers"] == ["Zimri-Lim"]
    assert document["correspondents"] == ["Zimri-Lim"]
    assert document["city"] == "Mari"
    assert document["locality"] == "Syria"
    assert document["period"] == "Old Babylonian"
    assert document["sub_period"] is None
    assert document["languages"] == ["Akkadian"]
    other = documents[sample.tablet_without_instances.id]
    assert other["rulers"] == []
    assert other["identifiers"] == ["BM 12345"]


def test_tablet_documents_include_catalogue_numbers_and_other_names(
    sample: Sample,
) -> None:
    add_catalogue_values(sample)

    document = {doc["id"]: doc for doc in tablet_documents()}[sample.tablet.id]

    assert document["identifiers"] == ["P000001", "BM 000001", "Q000002"]
    assert document["city_names"] == ["Tell Hariri"]
    assert document["year"] == "1761 BC"
    assert document["eponym"] == "Ashur-dan"


@pytest.mark.parametrize("query", ["P000001", "Q000002", "Tell Hariri", "ashur-dan"])
def test_search_finds_tablets_by_catalogue_numbers_and_other_names(
    sample: Sample, query: str
) -> None:
    add_catalogue_values(sample)

    assert search_records(query, limit=50).tablet_ids == [sample.tablet.id]


def test_search_makes_the_search_tables_if_they_do_not_exist(sample: Sample) -> None:
    results = search_records("horizontal", limit=50)

    assert results.sign_ids == [sample.sign.id]
    assert db.session.scalar(text(f"SELECT count(*) FROM {SIGN_TABLE}")) == 2


def test_search_makes_the_search_tables_again_if_their_fields_changed(
    sample: Sample,
) -> None:
    rebuild()
    db.session.execute(text(f"DROP TABLE {TABLET_TABLE}"))
    db.session.execute(
        text(
            f"CREATE VIRTUAL TABLE {TABLET_TABLE}"
            " USING fts5(museum_number, tokenize='trigram')"
        )
    )
    db.session.commit()

    assert search_records("mari", limit=50).tablet_ids == [sample.tablet.id]


@pytest.mark.parametrize(
    ("query", "museum_numbers"),
    [
        ("zimri", ["A.1"]),
        ("STONE", ["BM_12345"]),
        ("Mari", ["A.1"]),
        ("barley", ["A.1"]),
        ("old babylonian", ["A.1", "BM_12345"]),
        ("akkadian", ["A.1"]),
        ("BM 12345", ["BM_12345"]),
    ],
)
def test_search_finds_tablets_by_their_details(
    sample: Sample, query: str, museum_numbers: list[str]
) -> None:
    ids = {
        sample.tablet.id: "A.1",
        sample.tablet_without_instances.id: "BM_12345",
    }

    results = search_records(query, limit=50)

    assert [ids[i] for i in results.tablet_ids] == museum_numbers


def test_short_queries_find_values_that_contain_them(sample: Sample) -> None:
    assert sign_refs("aš") == ["AŠ"]
    assert search_records("A.", limit=50).tablet_ids == [sample.tablet.id]


def test_exact_names_rank_before_names_that_contain_the_query(app: Flask) -> None:
    add_signs("|GIR₃~c×ŠE₃|", "GIR₃@g~a", "GIR₃")

    assert sign_refs("gir3") == ["GIR₃", "GIR₃@g~a", "|GIR₃~c×ŠE₃|"]


def test_search_keeps_s_and_s_caron_apart(app: Flask) -> None:
    add_signs("SA₃", "ŠA₃", "SA", "ŠA")

    assert sign_refs("ŠA₃") == ["ŠA₃"]
    assert sign_refs("sa₃") == ["SA₃"]
    assert sign_refs("ša") == ["ŠA", "ŠA₃"]


def test_search_counts_the_matches_beyond_the_limit(app: Flask) -> None:
    add_signs("NA", "NA₂", "NA₃", "NA₄", "NA₅")

    results = search_records("na", limit=2)

    assert len(results.sign_ids) == 2
    assert results.sign_count == 5


def test_rebuild_takes_new_records_into_the_search_tables(sample: Sample) -> None:
    rebuild()
    add_signs("KUŠU₂")
    assert sign_refs("kušu") == []

    rebuild()

    assert sign_refs("kušu") == ["KUŠU₂"]


@pytest.mark.parametrize(
    ("value", "expected"),
    [("GIR₃", "gir3"), ("ŠA", "ša"), ("|LU₂×KAD₃|", "|lu2×kad3|")],
)
def test_normalise_folds_case_and_subscript_digits(value: str, expected: str) -> None:
    assert normalise(value) == expected
