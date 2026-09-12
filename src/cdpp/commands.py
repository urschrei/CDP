"""Management commands. Run them as ``cdpp <command>``."""

from pathlib import Path

import click
from flask import current_app
from flask.cli import with_appcontext
from sqlalchemy import inspect

from cdpp.db import db
from cdpp.dump import DumpError, load_dump
from cdpp.search import (
    SIGNS,
    TABLETS,
    SearchUnavailable,
    search_index,
    sign_documents,
    tablet_documents,
)


@click.command("import-dump")
@click.argument(
    "dump",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    default=Path("db_dumps/glyph_latest.sql"),
)
@with_appcontext
def import_dump(dump: Path) -> None:
    """Replace all records with the contents of a MySQL dump.

    DUMP defaults to db_dumps/glyph_latest.sql. Run 'cdpp reindex' afterwards.
    """
    if not inspect(db.engine).has_table("tablet"):
        raise click.ClickException("The database has no schema. Run 'cdpp db upgrade'.")
    sql = dump.read_text(encoding="utf-8")
    try:
        with db.engine.begin() as connection:
            counts = load_dump(connection, db.metadata, sql)
    except DumpError as error:
        raise click.ClickException(f"{dump}: {error}") from error
    for table, count in sorted(counts.items()):
        click.echo(f"{table:<22}{count:>7}")
    click.echo(f"Imported {sum(counts.values())} rows from {dump}.")


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
