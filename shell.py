#!/usr/bin/env python
import os
from werkzeug import script
import readline

from flask import *
from app import *

os.environ['PYTHONINSPECT'] = 'True'

def make_shell():
    return dict(app=app)

if __name__ == "__main__":
    script.make_shell(make_shell, use_ipython=True)()
