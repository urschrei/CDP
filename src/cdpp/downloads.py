"""Downloads of sign photographs, with the records of their instances and tablets."""

import hashlib
import io
import re
from pathlib import Path

import click
from alembic.runtime.migration import MigrationContext
from flask import Blueprint, abort, current_app, send_file, url_for
from flask.cli import with_appcontext
from flask.typing import ResponseReturnValue
from sqlalchemy import select

from cdpp.db import db
from cdpp.models import Instance
from cdpp.photograph_metadata import (
    INSTANCE_OPTIONS,
    load_instance,
    photograph_record,
    photograph_with_metadata,
)
from cdpp.views import count_noun, media_root, photograph_path

bp = Blueprint("downloads", __name__)

# The address of the site on Fly.io.
SITE_URL = "https://cdpp.fly.dev"
# Spaces, and characters that some file systems do not allow in file names.
FILE_NAME_UNSAFE_RE = re.compile(r'[\\/:*?"<>|\s]+')


def download_name(instance: Instance) -> str:
    """Return the file name of a download, as in "BM_91082_ŠE_1234.png"."""
    parts = (instance.tablet.museum_number, instance.sign.sign_ref, str(instance.id))
    safe = (FILE_NAME_UNSAFE_RE.sub("-", part).strip("-") for part in parts)
    return "_".join(safe) + ".png"


def database_revision() -> str | None:
    """Return the migration revision of the database, or None if it has none."""
    return MigrationContext.configure(db.session.connection()).get_current_revision()


def tagged_photograph(instance: Instance, revision: str | None) -> bytes | None:
    """Return the photograph of ``instance`` with its record, or None without a file.

    ``revision`` is the migration revision of the database.
    """
    path = photograph_path(instance)
    if not path.is_file():
        return None
    record = photograph_record(
        instance,
        url_for("instances.instance", instance_id=instance.id, _external=True),
        url_for("cdpp.tablet", tablet_id=instance.tablet_id, _external=True),
        commit=current_app.config["COMMIT"],
        revision=revision,
    )
    return photograph_with_metadata(path.read_bytes(), record)


@bp.get("/instances/<int:instance_id>/photograph.png")
def photograph(instance_id: int) -> ResponseReturnValue:
    instance = load_instance(instance_id)
    data = (
        tagged_photograph(instance, database_revision())
        if instance is not None
        else None
    )
    if instance is None or data is None:
        abort(404)
    response = send_file(
        io.BytesIO(data),
        mimetype="image/png",
        as_attachment=True,
        download_name=download_name(instance),
        etag=hashlib.sha256(data).hexdigest(),
        # An edit changes the record, so a cache must ask for the current file.
        # The default maximum age is for the built assets.
        max_age=0,
    )
    response.cache_control.no_cache = True
    return response


@click.command("export-photographs")
@click.argument("directory", type=click.Path(file_okay=False, path_type=Path))
@click.option(
    "--site-url",
    default=SITE_URL,
    show_default=True,
    help="Address of the site, for the page addresses in the metadata.",
)
@with_appcontext
def export_photographs(directory: Path, site_url: str) -> None:
    """Write the photograph of each instance, with its record, to DIRECTORY.

    Each file has the name of the photograph file of the instance.
    """
    if directory.resolve() == media_root().resolve():
        raise click.UsageError(
            "DIRECTORY is the directory of the photographs. "
            "Its files must not contain the records."
        )
    directory.mkdir(parents=True, exist_ok=True)
    revision = database_revision()
    written = missing = 0
    instances = db.session.scalars(
        select(Instance).options(*INSTANCE_OPTIONS).order_by(Instance.id)
    )
    # The page addresses in the metadata need a request context.
    with current_app.test_request_context(base_url=site_url):
        for instance in instances:
            data = tagged_photograph(instance, revision)
            if data is None:
                missing += 1
                continue
            (directory / f"{instance.filename}.png").write_bytes(data)
            written += 1
    click.echo(f"Wrote {count_noun(written, 'photograph')} to {directory}.")
    click.echo(f"Instances without a photograph file: {missing}.")
