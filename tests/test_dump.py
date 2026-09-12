from datetime import datetime
from pathlib import Path

import pytest
from flask import Flask
from sqlalchemy import func, select

from cdpp.db import db
from cdpp.dump import DumpError, Insert, load_dump, parse_inserts
from cdpp.models import Instance, Medium, Sign, Tablet

DUMP_PATH = Path(__file__).parents[1] / "db_dumps" / "glyph_latest.sql"

# The tablet row comes before the rows it refers to, as in the original dump.
SMALL_DUMP = """
# Dump of table alembic_version
INSERT INTO `alembic_version` (`version_num`)
VALUES
\t('1a3861bf3a05');

INSERT INTO `tablet` (`id`, `timestamp`, `museum_number`, `medium_id`, `period_id`)
VALUES
\t(1,'2012-06-19 17:40:28',X'424D5F3934313638',2,8);

INSERT INTO `medium` (`id`, `name`)
VALUES
\t(2,X'636C6179');

INSERT INTO `period` (`id`, `name`, `from_date`, `to_date`)
VALUES
\t(8,'Old Babylonian','1900','1600');
"""


def test_parse_inserts_reads_each_value_type() -> None:
    sql = r"""
INSERT INTO `medium` (`id`, `name`)
VALUES
	(2,X'C5A0'),
	(3,'it''s \'stone\'\n'),
	(4,NULL),
	(5,'50\%');
"""
    assert list(parse_inserts(sql)) == [
        Insert(
            "medium",
            ("id", "name"),
            [(2, "Š"), (3, "it's 'stone'\n"), (4, None), (5, "50\\%")],
        )
    ]


def test_parse_inserts_reads_consecutive_statements() -> None:
    tables = [insert.table for insert in parse_inserts(SMALL_DUMP)]
    assert tables == ["alembic_version", "tablet", "medium", "period"]


def test_parse_inserts_rejects_a_row_of_the_wrong_width() -> None:
    sql = "INSERT INTO `medium` (`id`, `name`) VALUES\n(1);"
    with pytest.raises(DumpError, match="expected 2 values, found 1 at line 2"):
        list(parse_inserts(sql))


def test_parse_inserts_rejects_an_unterminated_statement() -> None:
    sql = "INSERT INTO `medium` (`id`, `name`) VALUES (1, 'clay')"
    with pytest.raises(DumpError, match="unexpected input"):
        list(parse_inserts(sql))


def test_load_dump_inserts_rows(app: Flask) -> None:
    with db.engine.begin() as connection:
        counts = load_dump(connection, db.metadata, SMALL_DUMP)

    assert counts == {"tablet": 1, "medium": 1, "period": 1}
    tablet = db.session.get_one(Tablet, 1)
    assert tablet.museum_number == "BM_94168"
    assert tablet.medium.name == "clay"
    assert tablet.timestamp == datetime(2012, 6, 19, 17, 40, 28)


def test_load_dump_replaces_existing_rows(app: Flask) -> None:
    db.session.add(Medium(id=99, name="wax"))
    db.session.commit()

    with db.engine.begin() as connection:
        load_dump(connection, db.metadata, SMALL_DUMP)

    assert db.session.scalars(select(Medium.name)).all() == ["clay"]


def test_load_dump_rejects_broken_foreign_keys(app: Flask) -> None:
    sql = SMALL_DUMP.replace("(2,X'636C6179')", "(3,X'636C6179')")
    with (
        pytest.raises(DumpError, match="refers to a missing 'medium' row"),
        db.engine.begin() as connection,
    ):
        load_dump(connection, db.metadata, sql)

    assert db.session.scalar(select(func.count()).select_from(Tablet)) == 0


def test_load_dump_rejects_unknown_tables(app: Flask) -> None:
    sql = "INSERT INTO `tablets` (`id`) VALUES (1);"
    with (
        pytest.raises(DumpError, match="unknown table 'tablets'"),
        db.engine.begin() as connection,
    ):
        load_dump(connection, db.metadata, sql)


def test_load_dump_imports_the_project_dump(app: Flask) -> None:
    with db.engine.begin() as connection:
        counts = load_dump(
            connection, db.metadata, DUMP_PATH.read_text(encoding="utf-8")
        )

    assert counts["tablet"] == 228
    assert counts["sign"] == 3440
    assert counts["instance"] == 11404
    assert counts["cdp"] == 4776
    count = select(func.count())
    assert db.session.scalar(count.select_from(Instance)) == 11404
    assert db.session.scalar(count.select_from(Sign)) == 3440
