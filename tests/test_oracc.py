from pathlib import Path

import pytest
from flask import Flask
from sqlalchemy import func, select

from cdpp.db import db
from cdpp.models import Cdp, OraccListNumber, OraccSign, Sign, SignName
from cdpp.oracc import number_forms, parse_osl, renderable_cuneiform, sign_glyphs

ASL = """\
@project osl
@listdef MZL 1-907
@sign A
@list\tLAK795
@oid\to0000087
@list\tMZL839
@list\tU+12000
@ucun\t𒀀
@link\teBL A https://www.ebl.lmu.de/signs/A
@v\ta
@form |A.A|
@oid\to0000088
@list\tMZL839a
@@
@form- |A.OLD|
@oid\to0000089
@@
@end sign
@sign- OLD
@oid\to0000090
@form |OLD.FORM|
@oid\to0000091
@@
@end sign
@sign |NINDA₂×GUD|
@oid\to0000100
@link\teBL |NINDA₂×GUD| https://www.ebl.lmu.de/signs/|NINDA₂×GUD|
@end sign
@sign NOID
@list\tMZL001
@end sign
"""


def test_parse_osl_reads_signs_and_forms_that_are_not_removed() -> None:
    entries = parse_osl(ASL.splitlines())

    assert [(entry.name, entry.oid) for entry in entries] == [
        ("A", "o0000087"),
        ("|A.A|", "o0000088"),
        ("|NINDA₂×GUD|", "o0000100"),
    ]
    assert entries[0].numbers == [("LAK", "795"), ("MZL", "839")]
    assert entries[1].numbers == [("MZL", "839a")]


def test_parse_osl_encodes_ebl_links() -> None:
    entries = parse_osl(ASL.splitlines())

    assert entries[0].ebl_url == "https://www.ebl.lmu.de/signs/A"
    assert entries[1].ebl_url is None
    assert entries[2].ebl_url == (
        "https://www.ebl.lmu.de/signs/%7CNINDA%E2%82%82%C3%97GUD%7C"
    )


def test_parse_osl_reads_the_unicode_cuneiform() -> None:
    entries = parse_osl(ASL.splitlines())

    assert [entry.cuneiform for entry in entries] == ["𒀀", None, None]


@pytest.mark.parametrize(
    ("number", "forms"),
    [
        ("5", ("005", "5")),
        ("057", ("057",)),
        ("219a", ("219a",)),
        ("1000", ("1000",)),
        ("172?", ("172?",)),
        ("N-1", ("N-1",)),
    ],
)
def test_number_forms(number: str, forms: tuple[str, ...]) -> None:
    assert number_forms(number) == forms


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("𒀀", "𒀀"),
        ("𒀀𒀊", "𒀀𒀊"),
        ("X𒀀", None),
        ("\U000f0085", None),
        ("", None),
        (None, None),
    ],
)
def test_renderable_cuneiform_needs_characters_that_the_font_has(
    value: str | None, expected: str | None
) -> None:
    assert renderable_cuneiform(value) == expected


def test_sign_glyphs_use_the_sign_name_then_the_oracc_names(app: Flask) -> None:
    db.session.add_all(
        [
            OraccSign(oid="o1", name="A", cuneiform="𒀀"),
            OraccSign(oid="o2", name="|A.A|", cuneiform="𒀀𒀀"),
            OraccSign(oid="o3", name="TWO", cuneiform="𒀭"),
            OraccSign(oid="o4", name="TWO", cuneiform="𒁀"),
            OraccSign(oid="o5", name="PRIVATE", cuneiform="\U000f0085"),
        ]
    )
    by_name = Sign(sign_ref="A")
    by_record = Sign(
        sign_ref="AA", cdp_records=[Cdp(names=[SignName(source="oracc", name="|A.A|")])]
    )
    signs = [by_name, by_record, Sign(sign_ref="TWO"), Sign(sign_ref="PRIVATE")]
    db.session.add_all([*signs, Sign(sign_ref="NONE")])
    db.session.commit()

    glyphs = sign_glyphs(sign.id for sign in db.session.scalars(select(Sign)))

    assert glyphs == {by_name.id: "𒀀", by_record.id: "𒀀𒀀"}


def test_import_oracc_signs_replaces_the_snapshot(app: Flask, tmp_path: Path) -> None:
    osl = tmp_path / "osl.asl"
    osl.write_text(ASL, encoding="utf-8")
    runner = app.test_cli_runner()

    for _ in range(2):
        result = runner.invoke(args=["import-oracc-signs", str(osl)])
        assert result.exit_code == 0, result.output

    assert db.session.scalar(select(func.count()).select_from(OraccSign)) == 3
    assert db.session.scalar(select(func.count()).select_from(OraccListNumber)) == 3
    stored = select(OraccSign.cuneiform).where(OraccSign.oid == "o0000087")
    assert db.session.scalar(stored) == "𒀀"
