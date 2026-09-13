"""Management commands. Run them as ``cdpp <command>``."""

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

import click
from flask import current_app
from flask.cli import with_appcontext
from flask_migrate import upgrade
from sqlalchemy import inspect

from cdpp.db import db
from cdpp.oracc import OSL_URL, read_osl, replace_snapshot
from cdpp.search import (
    SIGNS,
    TABLETS,
    SearchUnavailable,
    search_index,
    sign_documents,
    tablet_documents,
)

DATA_DUMP = Path("db_dumps/cdpp.sql")


@click.command("dump-data")
@click.argument(
    "path", type=click.Path(dir_okay=False, path_type=Path), default=DATA_DUMP
)
@with_appcontext
def dump_data(path: Path) -> None:
    """Write the schema and all records of the database to an SQL file.

    PATH defaults to db_dumps/cdpp.sql.
    """
    with sqlite_connection() as connection:
        # iterdump writes the tables in alphabetical order, not in the order
        # of their foreign keys.
        lines = ["PRAGMA foreign_keys = OFF;", *connection.iterdump()]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    click.echo(f"Wrote the database to {path}.")


@click.command("load-data")
@click.argument(
    "path",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    default=DATA_DUMP,
)
@click.option("--replace", is_flag=True, help="Delete the existing tables first.")
@with_appcontext
def load_data(path: Path, replace: bool) -> None:
    """Create the database from an SQL file, then apply newer migrations.

    PATH defaults to db_dumps/cdpp.sql. Run 'cdpp reindex' afterwards.
    """
    if inspect(db.engine).get_table_names() and not replace:
        raise click.ClickException(
            "The database already has tables. Use --replace to delete them first."
        )
    sql = path.read_text(encoding="utf-8")
    with sqlite_connection() as connection:
        connection.execute("PRAGMA foreign_keys = OFF")
        tables = connection.execute(
            "SELECT name FROM sqlite_schema"
            " WHERE type = 'table' AND name NOT LIKE 'sqlite_%'"
        ).fetchall()
        for (table,) in tables:
            connection.execute(f'DROP TABLE "{table}"')
        connection.executescript(sql)
        violations = connection.execute("PRAGMA foreign_key_check").fetchall()
        connection.execute("PRAGMA foreign_keys = ON")
    if violations:
        raise click.ClickException(
            f"{path} loaded, but {len(violations)} rows break foreign key constraints."
        )
    click.echo(f"Loaded {path}.")
    upgrade()


@click.command("import-oracc-signs")
@click.argument("source", default=OSL_URL)
@with_appcontext
def import_oracc_signs(source: str) -> None:
    """Replace the snapshot of the Oracc Sign List.

    SOURCE is a path or a URL of osl.asl, and defaults to the file in the
    repository of the Oracc Sign List. Run 'cdpp dump-data' afterwards.
    """
    signs, numbers = replace_snapshot(read_osl(source))
    click.echo(f"Imported {signs} signs and forms, with {numbers} list numbers.")


@click.command("reindex")
@with_appcontext
def reindex() -> None:
    """Rebuild the Meilisearch indexes from the database."""
    index = search_index()
    batches = {SIGNS: sign_documents(), TABLETS: tablet_documents()}
    for name, documents in batches.items():
        try:
            index.replace_documents(name, documents)
        except SearchUnavailable as error:
            url = current_app.config["MEILISEARCH_URL"]
            raise click.ClickException(f"Meilisearch at {url}: {error}") from error
        click.echo(f"Indexed {len(documents)} {name}.")


@contextmanager
def sqlite_connection() -> Iterator[sqlite3.Connection]:
    """Yield the SQLite connection of a connection from the engine's pool."""
    if db.engine.dialect.name != "sqlite":
        raise click.ClickException("This command works only with SQLite databases.")
    pooled = db.engine.raw_connection()
    try:
        connection = pooled.driver_connection
        assert isinstance(connection, sqlite3.Connection)
        yield connection
    finally:
        pooled.close()
