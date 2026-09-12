from pathlib import Path

import pytest
from alembic.script import ScriptDirectory
from flask import Flask
from flask_migrate import upgrade
from sqlalchemy import func, inspect, select, text

from cdpp import create_app
from cdpp.db import db
from cdpp.models import Medium, Period, Tablet


def file_app(database: Path) -> Flask:
    return create_app(
        {"TESTING": True, "SQLALCHEMY_DATABASE_URI": f"sqlite:///{database}"}
    )


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
        count = select(func.count()).select_from(Tablet)
        assert db.session.scalar(count) == 1


def test_load_data_migrates_the_project_dump_to_the_latest_revision(
    tmp_path: Path,
) -> None:
    # The project dump has rows that refer to each other, so this test also
    # checks that migrations can change tables that other tables refer to.
    dump = Path(__file__).parents[1] / "db_dumps" / "cdpp.sql"
    target = file_app(tmp_path / "target.sqlite3")

    result = target.test_cli_runner().invoke(args=["load-data", str(dump)])

    assert result.exit_code == 0, result.output
    with target.app_context():
        config = target.extensions["migrate"].migrate.get_config()
        head = ScriptDirectory.from_config(config).get_current_head()
        revision = db.session.scalar(text("SELECT version_num FROM alembic_version"))
        assert revision == head
        assert db.session.scalar(select(func.count()).select_from(Tablet)) == 228
