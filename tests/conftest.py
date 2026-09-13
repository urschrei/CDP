from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

import pytest
from flask import Flask
from flask.testing import FlaskClient

from cdpp import create_app
from cdpp.db import db
from cdpp.models import (
    Cdp,
    City,
    Correspondent,
    Genre,
    Instance,
    Language,
    Line,
    Locality,
    Medium,
    Period,
    Ruler,
    Sign,
    SignList,
    SignListEntry,
    SignName,
    Surface,
    Tablet,
)


@pytest.fixture
def app(tmp_path: Path) -> Iterator[Flask]:
    (tmp_path / "instance").mkdir()
    app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite://",
            "MEDIA_ROOT": str(tmp_path),
        }
    )
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    return app.test_client()


@dataclass(frozen=True)
class Sample:
    tablet: Tablet
    tablet_without_instances: Tablet
    sign: Sign
    sign_without_records: Sign


@pytest.fixture
def sample(app: Flask) -> Sample:
    old_babylonian = Period(name="Old Babylonian", from_date="1900", to_date="1600")
    syria = Locality(area="Syria")
    zimri_lim = Ruler(name="Zimri-Lim")
    line_1 = Line(number="1")
    meszl = SignList(name="MesZL", position=1)
    zatu = SignList(name="ZATU", position=3)
    lak = SignList(name="LAK", position=4)

    sign = Sign(
        sign_ref="AŠ",
        cdp_records=[
            Cdp(
                form_name="a",
                names=[
                    SignName(source="oracc", name="AŠ"),
                    SignName(source="description", name="horizontal wedge"),
                ],
                sign_list_entries=[SignListEntry(sign_list=meszl, number="1")],
            ),
            Cdp(
                form_name="b",
                sign_list_entries=[SignListEntry(sign_list=lak, number="2")],
            ),
        ],
    )
    tablet = Tablet(
        museum_number="A.1",
        medium=Medium(name="clay"),
        period=old_babylonian,
        city=City(name="Mari", locality=syria),
        locality=syria,
        genre=Genre(name="letter"),
        rulers=[zimri_lim],
        sent_from=Correspondent(ruler=zimri_lim),
        notes="Letter about barley",
        instances=[
            Instance(
                sign=sign,
                surface=Surface(name="obverse"),
                line=line_1,
                filename="I_1",
                language=Language(name="Akkadian"),
            ),
            Instance(sign=sign, line=line_1, filename="I_2"),
        ],
    )
    tablet_without_instances = Tablet(
        museum_number="BM_12345", medium=Medium(name="stone"), period=old_babylonian
    )
    sign_without_records = Sign(sign_ref="ZA")

    db.session.add_all([tablet, tablet_without_instances, sign_without_records, zatu])
    db.session.commit()
    sample = Sample(tablet, tablet_without_instances, sign, sign_without_records)
    # The test client shares this session. Detach the records, so that each
    # test starts with an empty identity map, as each request does. Refresh
    # them first, so that their column values stay readable.
    for record in (tablet, tablet_without_instances, sign, sign_without_records):
        db.session.refresh(record)
    db.session.expunge_all()
    return sample
