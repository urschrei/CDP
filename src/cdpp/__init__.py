"""Cuneiform Digital Palaeography Project web application."""

from collections.abc import Mapping
from datetime import timedelta
from pathlib import Path
from typing import Any

from flask import Flask

import cdpp.models  # noqa: F401 (registers the tables on the metadata)
from cdpp import assets, search, views
from cdpp.commands import import_dump, reindex
from cdpp.db import db, migrate

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def create_app(config: Mapping[str, Any] | None = None) -> Flask:
    """Create and configure the application.

    Settings come from the defaults below, then from environment variables
    with the ``CDPP_`` prefix (for example ``CDPP_MEILISEARCH_URL``), then
    from ``config``.
    """
    app = Flask(__name__, instance_path=str(PROJECT_ROOT / "instance"))
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    app.config.from_mapping(
        SQLALCHEMY_DATABASE_URI=f"sqlite:///{Path(app.instance_path) / 'cdpp.sqlite3'}",
        MEILISEARCH_URL="http://127.0.0.1:7700",
        MEILISEARCH_API_KEY=None,
        MEILISEARCH_INDEX_PREFIX="cdpp_",
        MEDIA_ROOT=str(PROJECT_ROOT / "media"),
        # The static folder contains only built assets. Their URLs change when
        # their content changes.
        SEND_FILE_MAX_AGE_DEFAULT=timedelta(days=365),
    )
    app.config.from_prefixed_env("CDPP")
    if config is not None:
        app.config.from_mapping(config)

    db.init_app(app)
    migrate.init_app(app, db)
    assets.init_app(app)
    search.init_app(app)
    app.register_blueprint(views.bp)
    app.cli.add_command(import_dump)
    app.cli.add_command(reindex)
    return app
