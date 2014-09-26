#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
from flask import *
from app import app

from flask.ext.sqlalchemy import SQLAlchemy
from apps.glyph.models import *

app.testing = True
client = app.test_client()
ctx = app.test_request_context()
ctx.push()

db.create_all()
