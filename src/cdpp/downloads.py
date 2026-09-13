"""Downloads of sign photographs, with the records of their instances and tablets."""

import hashlib
import io
import re

from flask import Blueprint, abort, send_file, url_for
from flask.typing import ResponseReturnValue

from cdpp.models import Instance
from cdpp.photograph_metadata import (
    load_instance,
    photograph_record,
    photograph_with_metadata,
)
from cdpp.views import photograph_path

bp = Blueprint("downloads", __name__)

# Spaces, and characters that some file systems do not allow in file names.
FILE_NAME_UNSAFE_RE = re.compile(r'[\\/:*?"<>|\s]+')


def download_name(instance: Instance) -> str:
    """Return the file name of a download, as in "BM_91082_ŠE_1234.png"."""
    parts = (instance.tablet.museum_number, instance.sign.sign_ref, str(instance.id))
    safe = (FILE_NAME_UNSAFE_RE.sub("-", part).strip("-") for part in parts)
    return "_".join(safe) + ".png"


def tagged_photograph(instance: Instance) -> bytes | None:
    """Return the photograph of ``instance`` with its record, or None without a file."""
    path = photograph_path(instance)
    if not path.is_file():
        return None
    record = photograph_record(
        instance,
        url_for("instances.instance", instance_id=instance.id, _external=True),
        url_for("cdpp.tablet", tablet_id=instance.tablet_id, _external=True),
    )
    return photograph_with_metadata(path.read_bytes(), record)


@bp.get("/instances/<int:instance_id>/photograph.png")
def photograph(instance_id: int) -> ResponseReturnValue:
    instance = load_instance(instance_id)
    data = tagged_photograph(instance) if instance is not None else None
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
