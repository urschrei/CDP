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
    Description,
    Genre,
    Instance,
    Language,
    Line,
    Locality,
    Medium,
    Oracc,
    Period,
    Ruler,
    Sign,
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

    sign = Sign(
        sign_ref="AŠ",
        cdp_records=[
            Cdp(
                form_name="a",
                MesZL="1",
                oracc=Oracc(sign_ref="AŠ"),
                description=Description(sign_ref="horizontal wedge"),
            ),
            Cdp(form_name="b", LAK="2"),
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
                languages=[Language(name="Akkadian")],
            ),
            Instance(sign=sign, line=line_1, filename="I_2"),
        ],
    )
    tablet_without_instances = Tablet(
        museum_number="BM_12345", medium=Medium(name="stone"), period=old_babylonian
    )
    sign_without_records = Sign(sign_ref="ZA")

    db.session.add_all([tablet, tablet_without_instances, sign_without_records])
    db.session.commit()
    return Sample(tablet, tablet_without_instances, sign, sign_without_records)
