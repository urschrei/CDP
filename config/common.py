# no debugging by default - this is overriden in run.py for local dev
DEBUG = False

# currently the same for all environments
SQLALCHEMY_DATABASE_URI = 'mysql+mysqldb://root:@127.0.0.1/glyph?charset=utf8&use_unicode=0'

# os.urandom(128).encode('hex') should do the trick
SECRET_KEY = 'ce975af04b05782e6de27639bb0a64c9580efd20e03ed900c8d5014b35a9cdad161d5222533e7b63098371bbfb2f99a9b85c7a4b9fbff1662ba67069f743217376cfc4bdfbbd0109d06d63684cbf4d1cf237a02313e6d43887fe74635001da532fdd7f0b4372e9e828556b689819513673cda3cee6a5402a0da6fcb14d3a827f'
