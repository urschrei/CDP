from pathlib import Path

import pytest
from flask import Flask

from cdpp.cdli_comparison import (
    SECTIONS,
    city_agrees,
    languages_agree,
    material_agrees,
    object_type_agrees,
    period_agrees,
    replace_sections,
)
from cdpp.db import db
from cdpp.models import CdliArtifact
from tests.conftest import Sample


@pytest.mark.parametrize(
    ("period", "sub_period", "cdli_period", "agrees"),
    [
        ("Old Babylonian", None, "Old Babylonian (ca. 1900-1600 BC)", True),
        (
            "Old Babylonian",
            "Late Old Babylonian",
            "Old Babylonian (ca. 1900-1600 BC)",
            True,
        ),
        (
            "Old Babylonian",
            "Early Old Babylonian",
            "Old Babylonian (ca. 1900-1600 BC)",
            False,
        ),
        ("Late Third Millennium", "Ur III", "Lagash II (ca. 2200-2100 BC)", False),
        # CDLI writes some dates with an en dash.
        ("Late Babylonian", "Achaemenid", "Achaemenid (547\u2013331 BC)", True),
        ("Neo-Assyrian", "Sargonid", "Neo-Assyrian (ca. 911-612 BC) ?", True),
        ("Middle Assyrian", None, "Middle Babylonian (ca. 1400-1100 BC)", False),
        ("Old Babylonian", None, "Harappan", False),
        ("Old Babylonian", None, "uncertain", None),
        ("Old Babylonian", None, None, None),
    ],
)
def test_period_agrees(
    period: str, sub_period: str | None, cdli_period: str | None, agrees: bool | None
) -> None:
    assert period_agrees(period, sub_period, cdli_period) is agrees


@pytest.mark.parametrize(
    ("city", "provenience", "agrees"),
    [
        ("Nippur", "Nippur (mod. Nuffar)", True),
        ("Kultepe", "Kanesh (mod. Kültepe)", True),
        ("Sippar", "Sippar-Yahrurum (mod. Tell Abu Habbah) ?", True),
        ("Ashur", "Assur (mod. Qalat Sherqat)", True),
        ("Nimrud", "Kalhu (mod. Nimrud)", True),
        ("Nineveh", "Sippar-Yahrurum (mod. Tell Abu Habbah)", False),
        ("Sippar", "uncertain (mod. Babylonia)", None),
        ("Ur", "", None),
    ],
)
def test_city_agrees(city: str, provenience: str, agrees: bool | None) -> None:
    assert city_agrees(city, provenience) is agrees


@pytest.mark.parametrize(
    ("text_vehicle", "object_type", "agrees"),
    [
        ("tablet", "Tablet", True),
        ("tablet", "tablet & envelope", True),
        ("cylinder seal", "seal (not impression)", True),
        ("architectural feature", "cone", False),
        ("stela", "other (see object remarks)", None),
    ],
)
def test_object_type_agrees(
    text_vehicle: str, object_type: str, agrees: bool | None
) -> None:
    assert object_type_agrees(text_vehicle, object_type) is agrees


@pytest.mark.parametrize(
    ("medium", "material", "agrees"),
    [
        ("stone", "stone: diorite", True),
        ("stone", "stone; soapstone", True),
        ("clay", "Clay", True),
        ("stone", "clay", False),
        ("clay", "", None),
    ],
)
def test_material_agrees(medium: str, material: str, agrees: bool | None) -> None:
    assert material_agrees(medium, material) is agrees


@pytest.mark.parametrize(
    ("languages", "cdli_language", "agrees"),
    [
        (["Akkadian", "Sumerian"], "Akkadian", True),
        (["Sumerian"], "Sumerian; Akkadian ?", True),
        (["Akkadian"], "Akkadian, Aramaic", True),
        (["Sumerian"], "Akkadian", False),
        (["Akkadian"], "undetermined", None),
        ([], "Sumerian", None),
    ],
)
def test_languages_agree(
    languages: list[str], cdli_language: str, agrees: bool | None
) -> None:
    assert languages_agree(languages, cdli_language) is agrees


def test_replace_sections_keeps_the_text_outside_the_sections() -> None:
    text = (
        "Question\n\n<!-- cdpp check-cdli: period -->\nold\n"
        "<!-- cdpp check-cdli: end -->\n\nAnswer: yes\n"
    )

    replaced = replace_sections(text, {"period": "new"})

    assert replaced == (
        "Question\n\n<!-- cdpp check-cdli: period -->\n\nnew\n\n"
        "<!-- cdpp check-cdli: end -->\n\nAnswer: yes\n"
    )
    assert replace_sections(replaced, {"period": "new"}) == replaced
    with pytest.raises(ValueError, match="check-cdli: city"):
        replace_sections(text, {"city": "new"})


def questions_file(path: Path) -> Path:
    sections = "".join(
        f"### {name}\n\n<!-- cdpp check-cdli: {name} -->\n"
        "<!-- cdpp check-cdli: end -->\n\nAnswer:\n\n"
        for name in SECTIONS
    )
    path.write_text(f"# Questions\n\n{sections}", encoding="utf-8")
    return path


def test_check_cdli_writes_the_tablets_that_do_not_agree(
    app: Flask, sample: Sample, tmp_path: Path
) -> None:
    tablet, other = sample.tablet, sample.tablet_without_instances
    db.session.add_all(
        [
            CdliArtifact(
                tablet_id=tablet.id,
                p_number="P000001",
                designation="A 1",
                period="Ur III (ca. 2100-2000 BC)",
                provenience="Mari (mod. Tell Hariri)",
                object_type="tablet",
                material="stone",
                language="Sumerian",
            ),
            CdliArtifact(
                tablet_id=other.id,
                p_number="P000002",
                designation="BM 12345",
                period="Old Babylonian (ca. 1900-1600 BC)",
                provenience="Sippar-Yahrurum (mod. Tell Abu Habbah) ?",
                material="stone: diorite",
            ),
        ]
    )
    db.session.commit()
    path = questions_file(tmp_path / "questions.md")
    runner = app.test_cli_runner()

    result = runner.invoke(args=["check-cdli", str(path)])

    assert result.exit_code == 0, result.output
    assert result.output.splitlines() == [
        "period: 1 tablets",
        "city: 1 tablets",
        "object: 1 tablets",
        "language: 1 tablets",
    ]
    text = path.read_text(encoding="utf-8")
    page = f"`/tablets/{tablet.id}`"
    assert (
        f"| A.1 | {page} | Old Babylonian |  | P000001 | Ur III (ca. 2100-2000 BC) |"
        in text
    )
    assert (
        f"| BM_12345 | `/tablets/{other.id}` | P000002 |"
        " Sippar-Yahrurum (mod. Tell Abu Habbah) ? |" in text
    )
    assert f"| A.1 | {page} |  | clay | P000001 | tablet | stone |" in text
    assert f"| A.1 | {page} | Akkadian | P000001 | Sumerian |" in text
    assert f"| A.1 | {page} | 1 | 2 | Akkadian | P000001 | Sumerian |" in text
    assert text.count("Answer:") == len(SECTIONS)

    runner.invoke(args=["check-cdli", str(path)])

    assert path.read_text(encoding="utf-8") == text


def test_check_cdli_needs_the_sections(app: Flask, tmp_path: Path) -> None:
    path = tmp_path / "questions.md"
    path.write_text("# Questions\n", encoding="utf-8")

    result = app.test_cli_runner().invoke(args=["check-cdli", str(path)])

    assert result.exit_code != 0
    assert "No section starts with <!-- cdpp check-cdli: period -->" in result.output
