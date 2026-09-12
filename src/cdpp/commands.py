"""Management commands. Run them as ``cdpp <command>``."""

from pathlib import Path

import click
from flask.cli import with_appcontext
from sqlalchemy import inspect

from cdpp.db import db
from cdpp.dump import DumpError, load_dump


@click.command("import-dump")
@click.argument(
    "dump",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    default=Path("db_dumps/glyph_latest.sql"),
)
@with_appcontext
def import_dump(dump: Path) -> None:
    """Replace all records with the contents of a MySQL dump.

    DUMP defaults to db_dumps/glyph_latest.sql.
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
