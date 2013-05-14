from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declared_attr

db = SQLAlchemy()


class GlyphMixin(object):
    """
    Provides some common attributes to our models
    """

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    __table_args__ = {'mysql_engine': 'InnoDB'}
    __mapper_args__ = {'always_refresh': True}

    id = db.Column(db.Integer, primary_key=True)
