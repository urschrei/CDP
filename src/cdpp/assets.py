"""URLs for the built front-end assets in static/dist."""

import hashlib
from functools import lru_cache
from pathlib import Path

from flask import Flask, current_app, url_for


def init_app(app: Flask) -> None:
    app.add_template_global(asset_url)


def asset_url(filename: str) -> str:
    """Return the URL of a built asset, with a version from its content.

    The version changes when the file changes, so browsers can keep the asset
    in their cache for a long time.
    """
    path = Path(current_app.static_folder or "") / "dist" / filename
    version = _content_hash(path, path.stat().st_mtime_ns) if path.is_file() else None
    return url_for("static", filename=f"dist/{filename}", v=version)


@lru_cache(maxsize=16)
def _content_hash(path: Path, _mtime_ns: int) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:12]
