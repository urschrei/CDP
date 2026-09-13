from collections.abc import Callable
from datetime import datetime
from typing import Any

import pytest
from flask import Flask
from sqlalchemy import Table, delete, insert, select, update
from sqlalchemy.exc import IntegrityError, InvalidRequestError

import cdpp.models  # noqa: F401 (registers the tables on the metadata)
from cdpp.db import db
from cdpp.models import (
    Cdp,
    Change,
    ChangeSet,
    City,
    Correspondent,
    Entity,
    Eponym,
    Locality,
    Medium,
    NonRulerCorrespondent,
    Period,
    Reign,
    Ruler,
    Sign,
    SignName,
    SubPeriod,
    Tablet,
    Year,
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


@pytest.fixture
def consistent(app: Flask) -> dict[str, int]:
    """Add a tablet and a reign with consistent values, and return the IDs.

    Each "other_" record is a value that contradicts the others.
    """
    records: dict[str, Entity] = {
        "period": Period(name="Neo-Assyrian", from_date="911 BC", to_date="612 BC"),
        "other_period": Period(name="Old Babylonian", from_date="", to_date=""),
        "locality": Locality(area="Assyria"),
        "other_locality": Locality(area="Syria"),
        "eponym": Eponym(name="Sha-Nabu-shu"),
        "other_eponym": Eponym(name="Labasi"),
        "ruler": Ruler(name="Ashurbanipal"),
        "medium": Medium(name="clay"),
    }
    db.session.add_all(records.values())
    db.session.flush()
    ids = {name: record.id for name, record in records.items()}
    related: dict[str, Entity] = {
        "sub_period": SubPeriod(name="Sargonid", period_id=ids["period"]),
        "other_sub_period": SubPeriod(
            name="Late Old Babylonian", period_id=ids["other_period"]
        ),
        "city": City(name="Nineveh", locality_id=ids["locality"]),
        "year": Year(year="658 BC", eponym_id=ids["eponym"]),
    }
    db.session.add_all(related.values())
    db.session.flush()
    ids |= {name: record.id for name, record in related.items()}
    tablet = Tablet(
        museum_number="K.1",
        medium_id=ids["medium"],
        period_id=ids["period"],
        sub_period_id=ids["sub_period"],
        city_id=ids["city"],
        year_id=ids["year"],
        eponym_id=ids["eponym"],
    )
    reign = Reign(
        ruler_id=ids["ruler"],
        rim_ref="A.0.113",
        period_id=ids["period"],
        sub_period_id=ids["sub_period"],
    )
    db.session.add_all([tablet, reign])
    db.session.commit()
    return ids


@pytest.mark.parametrize(
    ("rule", "statement"),
    [
        (
            "tablet_sub_period",
            lambda ids: insert(Tablet).values(
                museum_number="K.2",
                medium_id=ids["medium"],
                period_id=ids["other_period"],
                sub_period_id=ids["sub_period"],
            ),
        ),
        (
            "tablet_sub_period",
            lambda ids: update(Tablet).values(period_id=ids["other_period"]),
        ),
        (
            "tablet_sub_period",
            lambda ids: update(Tablet).values(sub_period_id=ids["other_sub_period"]),
        ),
        (
            "reign_sub_period",
            lambda ids: update(Reign).values(sub_period_id=ids["other_sub_period"]),
        ),
        (
            "ck_tablet_city_or_locality",
            lambda ids: update(Tablet).values(locality_id=ids["other_locality"]),
        ),
        (
            "tablet_year_eponym",
            lambda ids: update(Tablet).values(eponym_id=ids["other_eponym"]),
        ),
        (
            "sub_period_period",
            lambda ids: (
                update(SubPeriod)
                .where(SubPeriod.id == ids["sub_period"])
                .values(period_id=ids["other_period"])
            ),
        ),
        ("year_eponym", lambda ids: update(Year).values(eponym_id=ids["other_eponym"])),
    ],
)
def test_values_stored_twice_cannot_contradict_each_other(
    consistent: dict[str, int], rule: str, statement: Callable[[dict[str, int]], Any]
) -> None:
    with pytest.raises(IntegrityError, match=rule):
        db.session.execute(statement(consistent))


def test_changes_that_keep_the_values_consistent_are_allowed(
    consistent: dict[str, int],
) -> None:
    ids = consistent
    statements = [
        # Without a sub-period, a tablet can have any period.
        update(Tablet).values(sub_period_id=None, period_id=ids["other_period"]),
        # Without a city, a tablet can have any locality.
        update(Tablet).values(city_id=None, locality_id=ids["other_locality"]),
        update(City).values(locality_id=ids["other_locality"]),
        update(Tablet).values(eponym_id=None),
        update(Year).values(eponym_id=ids["other_eponym"]),
        # A change to other columns does not check the rules.
        update(Tablet).values(notes="Checked"),
    ]

    for statement in statements:
        db.session.execute(statement)
    db.session.commit()


def test_the_locality_of_a_tablet_is_the_locality_of_its_city() -> None:
    assyria, syria = Locality(area="Assyria"), Locality(area="Syria")

    assert Tablet(city=City(name="Nineveh", locality=assyria)).locality is assyria
    assert Tablet(own_locality=syria).locality is syria
    assert Tablet(city=City(name="Adab")).locality is None


def test_sign_name_source_must_be_a_known_source(app: Flask) -> None:
    record = Cdp(sign=Sign(sign_ref="A"), names=[SignName(source="other", name="A")])
    db.session.add(record)

    with pytest.raises(IntegrityError, match="ck_sign_name_source"):
        db.session.flush()
