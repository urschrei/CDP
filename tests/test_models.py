import pytest
from flask import Flask
from sqlalchemy import Table, select
from sqlalchemy.exc import IntegrityError, InvalidRequestError

import cdpp.models  # noqa: F401 (registers the tables on the metadata)
from cdpp.db import db
from cdpp.models import (
    Cdp,
    Correspondent,
    Entity,
    Instance,
    NonRulerCorrespondent,
    Ruler,
    Sign,
    Tablet,
)
from tests.conftest import Sample


@pytest.mark.parametrize("table", db.metadata.sorted_tables, ids=lambda t: t.name)
def test_every_foreign_key_column_begins_an_index(table: Table) -> None:
    leading = {next(iter(index.columns)).name for index in table.indexes}
    leading.add(next(iter(table.primary_key.columns)).name)

    unindexed = {key.parent.name for key in table.foreign_keys} - leading

    assert not unindexed


@pytest.mark.parametrize(
    ("has_ruler", "has_non_ruler"),
    [(False, False), (True, True)],
    ids=["neither party", "both parties"],
)
def test_correspondent_needs_exactly_one_party(
    app: Flask, has_ruler: bool, has_non_ruler: bool
) -> None:
    correspondent = Correspondent(
        ruler=Ruler(name="Zimri-Lim") if has_ruler else None,
        non_ruler=NonRulerCorrespondent(name="Yasmah-Addu") if has_non_ruler else None,
    )
    db.session.add(correspondent)

    with pytest.raises(IntegrityError, match="ck_correspondent_one_party"):
        db.session.flush()


def test_correspondent_name_is_the_same_in_python_and_in_sql(app: Flask) -> None:
    db.session.add_all(
        [
            Correspondent(ruler=Ruler(name="Zimri-Lim")),
            Correspondent(non_ruler=NonRulerCorrespondent(name="Yasmah-Addu")),
        ]
    )
    db.session.commit()
    by_name = select(Correspondent).order_by(Correspondent.name)

    in_python = [correspondent.name for correspondent in db.session.scalars(by_name)]
    in_sql = db.session.scalars(
        select(Correspondent.name)
        .select_from(Correspondent)
        .order_by(Correspondent.name)
    )

    assert in_python == list(in_sql) == ["Yasmah-Addu", "Zimri-Lim"]


@pytest.mark.parametrize(
    ("model", "collection"),
    [
        (Tablet, "instances"),
        (Tablet, "rulers"),
        (Tablet, "recipients"),
        (Sign, "instances"),
        (Sign, "cdp_records"),
        (Cdp, "sign_list_entries"),
        (Instance, "languages"),
    ],
    ids=lambda value: value if isinstance(value, str) else value.__name__,
)
def test_unloaded_collections_raise_instead_of_querying(
    sample: Sample, model: type[Entity], collection: str
) -> None:
    db.session.expire_all()
    record = db.session.scalars(select(model).limit(1)).one()

    with pytest.raises(InvalidRequestError, match="raise_on_sql"):
        getattr(record, collection)
