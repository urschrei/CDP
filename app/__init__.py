#!/usr/bin/env python
""" Glyph main site """

import os

from flask import Flask, render_template, request, url_for, redirect

from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_pyfile('config/common.py')

if os.getenv('GLYPH_CONFIGURATION'):
    app.config.from_envvar('GLYPH_CONFIGURATION')

# attach DB
db = SQLAlchemy(app)
# import our own blueprints here if necessary
# from apps.foo.views import foo_app
# attach any blueprints
# app.register_blueprint(foo_app, url_prefix='/foo')


@app.route('/')
def index():
    """ Glyph homepage """
    return render_template('index.jinja')
