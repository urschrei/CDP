"""Cuneiform Digital Palaeography Project web application."""

from collections.abc import Mapping
from datetime import timedelta
from pathlib import Path
from typing import Any

from flask import Flask

import cdpp.models  # noqa: F401 (registers the tables on the metadata)
from cdpp import access, assets, editor, history, instances, views
from cdpp.catalogues import import_cdli, import_oracc_texts
from cdpp.commands import backup, dump_data, import_oracc_signs, load_data, reindex
from cdpp.db import db, migrate

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def create_app(config: Mapping[str, Any] | None = None) -> Flask:
    """Create and configure the application.

    Settings come from the defaults below, then from environment variables
    with the ``CDPP_`` prefix (for example ``CDPP_MEDIA_ROOT``), then from
    ``config``.
    """
    app = Flask(__name__, instance_path=str(PROJECT_ROOT / "instance"))
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    app.config.from_mapping(
        SQLALCHEMY_DATABASE_URI=f"sqlite:///{Path(app.instance_path) / 'cdpp.sqlite3'}",
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
    access.init_app(app)
    assets.init_app(app)
    for blueprint in (views.bp, editor.bp, history.bp, instances.bp):
        app.register_blueprint(blueprint)
    commands = (
        dump_data,
        load_data,
        backup,
        import_oracc_signs,
        import_cdli,
        import_oracc_texts,
        reindex,
    )
    for command in commands:
        app.cli.add_command(command)
    return app
