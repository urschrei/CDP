import os
import sys
from flask import *
from glyph import app, db

app.testing = True
client = app.test_client()
ctx = app.test_request_context()
ctx.push()
print "app and db have been imported.\nYou have a test client: client,\nand a test request context: ctx"
