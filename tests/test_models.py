from datetime import datetime

import pytest
from flask import Flask
from sqlalchemy import Table, delete, select, update
from sqlalchemy.exc import IntegrityError, InvalidRequestError

import cdpp.models  # noqa: F401 (registers the tables on the metadata)
from cdpp.db import db
from cdpp.models import (
    Cdp,
    Change,
    ChangeSet,
    Correspondent,
    Entity,
    NonRulerCorrespondent,
    Ruler,
    Sign,
    SignName,
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
        (Cdp, "names"),
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


def change_set(kind: str = "update") -> ChangeSet:
    return ChangeSet(
        author="JJT",
        created_at=datetime(2026, 9, 14, 9, 0),
        changes=[
            Change(
                kind=kind,
                table_name="instance",
                record_id=1,
                field="line_id",
                old_value=None,
                new_value=2,
            )
        ],
    )


def test_change_sets_and_changes_cannot_be_changed_or_deleted(app: Flask) -> None:
    db.session.add(change_set())
    db.session.commit()
    statements = [
        update(ChangeSet).values(author="Someone else"),
        update(Change).values(new_value=3),
        delete(Change),
        delete(ChangeSet),
    ]

    for statement in statements:
        with pytest.raises(IntegrityError, match="cannot be changed or deleted"):
            db.session.execute(statement)
        db.session.rollback()


def test_change_kind_must_be_insert_or_update(app: Flask) -> None:
    db.session.add(change_set(kind="delete"))

    with pytest.raises(IntegrityError, match="ck_change_kind"):
        db.session.flush()


def test_sign_name_source_must_be_a_known_source(app: Flask) -> None:
    record = Cdp(sign=Sign(sign_ref="A"), names=[SignName(source="other", name="A")])
    db.session.add(record)

    with pytest.raises(IntegrityError, match="ck_sign_name_source"):
        db.session.flush()
