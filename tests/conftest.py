from collections.abc import Iterator

import pytest
from flask import Flask

from cdpp import create_app
from cdpp.db import db


@pytest.fixture
def app() -> Iterator[Flask]:
    app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite://"})
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()
