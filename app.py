#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Glyph main site """

import os

from flask import Flask, render_template

from flask.ext.assets import Environment
from webassets.loaders import YAMLLoader

app = Flask(__name__)

# attach DB. This assumes a Blueprint model
from apps.shared.models import db
db.init_app(app)

app.config.from_pyfile('config/common.py')

if os.getenv('GLYPH_CONFIGURATION'):
    app.config.from_envvar('GLYPH_CONFIGURATION')

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

from apps.glyph.views import glyph
from apps.glyph.forms import SearchForm
app.register_blueprint(glyph)


# Error handling
@app.errorhandler(404)
def page_not_found(error):
    """ 404 handler """
    return render_template(
        'errors/404.jinja', searchform=SearchForm()), 404


@app.errorhandler(500)
def application_error(error):
    """ 500 handler """
    return render_template(
        'errors/500.jinja', searchform=SearchForm()), 500
