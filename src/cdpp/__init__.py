"""Cuneiform Digital Palaeography Project web application."""

import os
from collections.abc import Mapping
from datetime import timedelta
from pathlib import Path
from typing import Any

from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

import cdpp.models  # noqa: F401 (registers the tables on the metadata)
from cdpp import access, assets, downloads, editor, history, instances, views
from cdpp.catalogues import import_cdli, import_oracc_texts
from cdpp.cdli_comparison import check_cdli
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
        TRUSTED_PROXIES=0,
    )
    app.config.from_prefixed_env("CDPP")
    # from_prefixed_env reads each value as JSON, so a commit such as 1234567e8
    # becomes a number. Keep the text. An empty value is no commit.
    app.config["COMMIT"] = os.environ.get("CDPP_COMMIT") or None
    if config is not None:
        app.config.from_mapping(config)
    # A proxy that receives HTTPS requests sends the scheme in
    # X-Forwarded-Proto. A client can also send this header, so use it only
    # behind the number of proxies in TRUSTED_PROXIES.
    if proxies := app.config["TRUSTED_PROXIES"]:
        # Flask documents this replacement of the method with middleware.
        app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=proxies)  # ty: ignore[invalid-assignment]

    db.init_app(app)
    migrate.init_app(app, db)
    access.init_app(app)
    assets.init_app(app)
    for blueprint in (views.bp, editor.bp, history.bp, instances.bp, downloads.bp):
        app.register_blueprint(blueprint)
    commands = (
        dump_data,
        load_data,
        backup,
        import_oracc_signs,
        import_cdli,
        import_oracc_texts,
        check_cdli,
        reindex,
        downloads.export_photographs,
    )
    for command in commands:
        app.cli.add_command(command)
    return app
