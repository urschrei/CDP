from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.sql import expression
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.types import DateTime

db = SQLAlchemy()


class utcnow(expression.FunctionElement):
    """ UTC Timestamp for compilation """
    type = DateTime()


# Define DB-specific utcnow() functions
@compiles(utcnow, 'postgresql')
def pg_utcnow(element, compiler, **kw):
    """ Postgres UTC Timestamp """
    return "TIMEZONE('utc', CURRENT_TIMESTAMP)"


@compiles(utcnow, 'mysql')
def my_utcnow(element, compiler, **kw):
    """ MySQL UTC Timestamp """
    return "UTC_TIMESTAMP()"


class GlyphMixin(object):
    """
    Provides some common attributes to our models
    """

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_collate': 'utf8mb4_bin',
        'mysql_default_charset': 'utf8mb4'
    }
    __mapper_args__ = {'always_refresh': True}

    id = db.Column(db.Integer, primary_key=True)
    # timestamp = db.Column(DateTime, nullable=False, server_default=utcnow())
