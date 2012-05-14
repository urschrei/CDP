#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Glyph main site """

import os

from flask import Flask, render_template

from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.assets import Environment, Bundle

app = Flask(__name__)
app.config.from_pyfile('config/common.py')

if os.getenv('GLYPH_CONFIGURATION'):
    app.config.from_envvar('GLYPH_CONFIGURATION')

# attach DB
db = SQLAlchemy(app)

# attach assets
assets = Environment(app)
js = Bundle(
    'http://ajax.googleapis.com/ajax/libs/jquery/1.7.2/jquery.min.js',
    'js/bootstrap.js',
    'js/jquery.easing.1.3.js',
    filters='yui_js',
    output='gen/packed.js')
assets.register('js_all', js)
css = Bundle(
        'http://yui.yahooapis.com/3.5.1/build/cssreset/cssreset-min.css',
        'css/bootstrap.css',
        'css/bootstrap-responsive.css',
        filters='yui_css',
        output='gen/packed.css')
assets.register('css_all', css)

# import our own blueprints here if necessary
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
