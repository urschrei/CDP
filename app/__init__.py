#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Glyph main site """

import os

from flask import Flask, render_template

from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.assets import Environment
from webassets.loaders import YAMLLoader

app = Flask(__name__)
app.config.from_pyfile('config/common.py')

if os.getenv('GLYPH_CONFIGURATION'):
    app.config.from_envvar('GLYPH_CONFIGURATION')

# attach DB
db = SQLAlchemy(app)

# attach assets
assets = Environment(app)
assets.versions = 'hash'

manifest_path = os.path.realpath(
        os.path.join(os.path.dirname(__file__), '.static-manifest'))
assets.manifest = 'file://%s' % manifest_path

bundles = YAMLLoader(os.path.realpath(
    os.path.join(os.path.dirname(__file__), 'assets.yml'))).load_bundles()

for bundle_name, bundle in bundles.items():
    assets.register(bundle_name, bundle)

## import our own blueprints here if necessary
# from apps.foo.views import foo_app
# attach any blueprints
# app.register_blueprint(foo_app, url_prefix='/foo')


@app.route('/')
def index():
    """ Glyph homepage """
    return render_template('index.jinja')


# Error handling
@app.errorhandler(404)
def page_not_found(error):
    """ 404 handler """
    return render_template(
        'errors/404.jinja'), 404


@app.errorhandler(500)
def application_error(error):
    """ 500 handler """
    return render_template(
        'errors/500.jinja'), 500

