from pathlib import Path

import pytest
from alembic.script import ScriptDirectory
from flask import Flask
from flask_migrate import downgrade, upgrade
from sqlalchemy import Select, func, inspect, select, text

from cdpp import create_app
from cdpp.db import db
from cdpp.models import Cdp, Medium, Period, SignList, SignListEntry, SignName, Tablet
from cdpp.search import rebuild

PROJECT_DUMP = Path(__file__).parents[1] / "db_dumps" / "cdpp.sql"


def file_app(database: Path) -> Flask:
    return create_app(
        {"TESTING": True, "SQLALCHEMY_DATABASE_URI": f"sqlite:///{database}"}
    )


def count(query: Select) -> int | None:
    return db.session.scalar(select(func.count()).select_from(query.subquery()))


@pytest.fixture
def dump_file(tmp_path: Path) -> Path:
    """Write a dump of a migrated database that contains one tablet."""
    dump = tmp_path / "cdpp.sql"
    source = file_app(tmp_path / "source.sqlite3")
    with source.app_context():
        upgrade()
        period = Period(name="Old Babylonian", from_date="1900", to_date="1600")
        db.session.add(
            Tablet(museum_number="A.1", medium=Medium(name="clay"), period=period)
        )
        db.session.commit()
        result = source.test_cli_runner().invoke(args=["dump-data", str(dump)])
    assert result.exit_code == 0, result.output
    return dump


@pytest.fixture
def project_app(tmp_path: Path) -> Flask:
    """Return an application with a database loaded from the project dump."""
    app = file_app(tmp_path / "project.sqlite3")
    result = app.test_cli_runner().invoke(args=["load-data", str(PROJECT_DUMP)])
    assert result.exit_code == 0, result.output
    return app


def test_dump_file_starts_with_foreign_keys_off(dump_file: Path) -> None:
    lines = dump_file.read_text(encoding="utf-8").splitlines()

    assert lines[0] == "PRAGMA foreign_keys = OFF;"
    assert 'INSERT INTO "tablet"' in "\n".join(lines)


def test_load_data_restores_the_records_and_the_migration_state(
    tmp_path: Path, dump_file: Path
) -> None:
    target = file_app(tmp_path / "target.sqlite3")

    result = target.test_cli_runner().invoke(args=["load-data", str(dump_file)])

    assert result.exit_code == 0, result.output
    with target.app_context():
        assert db.session.scalars(select(Tablet.museum_number)).all() == ["A.1"]
        assert inspect(db.engine).has_table("alembic_version")


def test_dump_data_leaves_out_the_search_tables(tmp_path: Path) -> None:
    source = file_app(tmp_path / "source.sqlite3")
    dump = tmp_path / "cdpp.sql"
    with source.app_context():
        upgrade()
        rebuild()
        assert inspect(db.engine).has_table("search_sign")
        result = source.test_cli_runner().invoke(args=["dump-data", str(dump)])

    assert result.exit_code == 0, result.output
    assert "search_" not in dump.read_text(encoding="utf-8")


def test_load_data_replaces_tables_only_with_the_option(
    tmp_path: Path, dump_file: Path
) -> None:
    target = file_app(tmp_path / "target.sqlite3")
    runner = target.test_cli_runner()
    assert runner.invoke(args=["load-data", str(dump_file)]).exit_code == 0

    refused = runner.invoke(args=["load-data", str(dump_file)])
    replaced = runner.invoke(args=["load-data", "--replace", str(dump_file)])

    assert refused.exit_code != 0
    assert "--replace" in refused.output
    assert replaced.exit_code == 0, replaced.output
    with target.app_context():
        assert count(select(Tablet)) == 1


def test_load_data_migrates_the_project_dump_to_the_latest_revision(
    project_app: Flask,
) -> None:
    # The project dump has rows that refer to each other, so this test also
    # checks that migrations can change tables that other tables refer to.
    with project_app.app_context():
        config = project_app.extensions["migrate"].migrate.get_config()
        head = ScriptDirectory.from_config(config).get_current_head()
        revision = db.session.scalar(text("SELECT version_num FROM alembic_version"))
        assert revision == head
        assert count(select(Tablet)) == 228
        assert count(select(SignListEntry)) == 25061
        assert count(select(SignName)) == 10549


def test_restored_2013_values_can_be_removed_and_restored_again(
    project_app: Flask,
) -> None:
    schroder_number = (
        select(SignListEntry.number)
        .join(SignList)
        .where(SignListEntry.cdp_id == 15, SignList.name == "Schroder VS 15")
    )
    form_descriptions = select(Cdp).where(Cdp.form_description.is_not(None))
    variant_names = select(Cdp).where(Cdp.variant_name.is_not(None))

    with project_app.app_context():
        downgrade(revision="6c1e9d2f7a38")
        assert count(select(SignListEntry)) == 16989
        assert count(form_descriptions) == 0
        assert count(variant_names) == 0

        upgrade()
        assert count(select(SignListEntry)) == 25061
        assert db.session.scalar(schroder_number) == "212"
        assert count(form_descriptions) == 144
        assert count(variant_names) == 2


def test_reigns_of_the_kings_of_alalakh_can_be_removed_and_added_again(
    project_app: Flask,
) -> None:
    reigns = text(
        "SELECT r.rim_ref, ru.name, c.name, p.name, first.year, last.year "
        "FROM reign r JOIN ruler ru ON ru.id = r.ruler_id "
        "JOIN dynasty d ON d.id = r.dynasty_id JOIN period p ON p.id = r.period_id "
        "LEFT JOIN city c ON c.id = r.city_id "
        "LEFT JOIN year first ON first.id = r.start_date "
        "LEFT JOIN year last ON last.id = r.end_date "
        "WHERE d.name = 'B.20' ORDER BY r.rim_ref"
    )
    expected = [
        ("B.20.1", "Idrimi", "Alalakh", "Middle Babylonian", "1470 BC", None),
        ("B.20.2", "Addu-nirari", "Alalakh", "Middle Babylonian", None, None),
        ("B.20.3", "Niqmepuh", "Alalakh", "Middle Babylonian", "1450 BC", "1425 BC"),
        ("B.20.4", "Ilim-ilimma II", "Alalakh", "Middle Babylonian", "1420 BC", None),
    ]

    with project_app.app_context():
        assert db.session.execute(reigns).all() == expected

        downgrade(revision="e7a2c94b1f05")
        assert db.session.execute(reigns).all() == []

        upgrade()
        assert db.session.execute(reigns).all() == expected


def test_alalah_merge_and_ruler_name_trim_can_be_undone_and_done_again(
    project_app: Flask,
) -> None:
    cities = text(
        "SELECT c.name, count(t.id) FROM city c "
        "LEFT JOIN tablet t ON t.city_id = c.id "
        "WHERE c.name IN ('Alalah', 'Alalakh') GROUP BY c.id ORDER BY c.name"
    )
    reign_cities = text(
        "SELECT c.name FROM reign r JOIN city c ON c.id = r.city_id "
        "WHERE r.rim_ref LIKE 'E.4.34.%'"
    )
    padded_rulers = text("SELECT count(*) FROM ruler WHERE name != trim(name)")

    with project_app.app_context():
        assert db.session.execute(cities).all() == [("Alalakh", 6)]
        assert db.session.scalars(reign_cities).all() == ["Alalakh"] * 3
        assert db.session.scalar(padded_rulers) == 0

        downgrade(revision="a3d5f8e1c702")
        assert db.session.execute(cities).all() == [("Alalah", 6), ("Alalakh", 0)]
        assert db.session.scalars(reign_cities).all() == ["Alalah"] * 3
        assert db.session.scalar(padded_rulers) == 5

        upgrade()
        assert db.session.execute(cities).all() == [("Alalakh", 6)]
        assert db.session.scalars(reign_cities).all() == ["Alalakh"] * 3
        assert db.session.scalar(padded_rulers) == 0


def test_period_and_locality_corrections_can_be_undone_and_done_again(
    project_app: Flask,
) -> None:
    checks = [
        text(
            "SELECT count(*) FROM tablet t JOIN sub_period s ON s.id = t.sub_period_id "
            "WHERE t.period_id != s.period_id"
        ),
        text(
            "SELECT count(*) FROM reign r JOIN sub_period s ON s.id = r.sub_period_id "
            "WHERE r.period_id != s.period_id"
        ),
        text(
            "SELECT count(*) FROM tablet t JOIN city c ON c.id = t.city_id "
            "WHERE c.locality_id IS NOT NULL AND t.locality_id IS NULL"
        ),
        text("SELECT count(*) FROM period WHERE name = 'ED'"),
    ]

    def contradictions() -> list[int | None]:
        return [db.session.scalar(check) for check in checks]

    with project_app.app_context():
        assert contradictions() == [0, 0, 0, 0]

        downgrade(revision="c9b4e2a7d613")
        assert contradictions() == [39, 50, 2, 1]

        upgrade()
        assert contradictions() == [0, 0, 0, 0]


def test_change_tables_and_their_triggers_come_and_go_with_the_migration(
    project_app: Flask,
) -> None:
    triggers = text(
        "SELECT name FROM sqlite_schema WHERE type = 'trigger' ORDER BY name"
    )
    expected = [
        "change_no_delete",
        "change_no_update",
        "change_set_no_delete",
        "change_set_no_update",
    ]

    with project_app.app_context():
        assert db.session.scalars(triggers).all() == expected

        downgrade(revision="f7a1c3e5b920")
        assert not inspect(db.engine).has_table("change_set")
        assert db.session.scalars(triggers).all() == []

        upgrade()
        assert db.session.scalars(triggers).all() == expected


def test_instance_languages_move_to_a_column_and_back(project_app: Flask) -> None:
    by_language = text(
        "SELECT l.name, count(*) FROM instance i "
        "JOIN language l ON l.id = i.language_id GROUP BY l.name ORDER BY l.name"
    )
    expected = [("Akkadian", 8368), ("Sumerian", 2671)]

    with project_app.app_context():
        assert db.session.execute(by_language).all() == expected
        assert not inspect(db.engine).has_table("instance_language")

        downgrade(revision="d4e6b1a9c285")
        association = text("SELECT count(*) FROM instance_language")
        assert db.session.scalar(association) == 11039
        columns = {
            column["name"] for column in inspect(db.engine).get_columns("instance")
        }
        assert "language_id" not in columns

        upgrade()
        assert db.session.execute(by_language).all() == expected
