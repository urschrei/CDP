"""The ``cdpp`` console command: Flask's CLI, bound to this application."""

from flask.cli import FlaskGroup

from cdpp import create_app

cli = FlaskGroup(create_app=create_app, help="Manage the CDPP web application.")
