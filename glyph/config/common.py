# no debugging by default - this is overriden in run.py for local dev
DEBUG = False

# currently the same for all environments
SQLALCHEMY_DATABASE_URI = 'mysql+mysqldb://root:@127.0.0.1/glyph?charset=utf8'

SECRET_KEY = 'Rameses'
