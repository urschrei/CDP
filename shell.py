import os
import sys
from flask import *
from glyph import app, db

app.testing = True
client = app.test_client()
ctx = app.test_request_context()
ctx.push()
