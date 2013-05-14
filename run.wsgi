activate_this = '/users/sth/dev/glyph/venv/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))
import sys
sys.path.insert(0, "/users/sth/dev/glyph")

from __init__ import app
application = app
