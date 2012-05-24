from glyph import db
from sqlalchemy.ext.declarative import declared_attr


class GlyphMixin(object):
    """
    Provides some common attributes to our tables
    """

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    __table_args__ = {'mysql_engine': 'InnoDB'}
    __mapper_args__= {'always_refresh': True}

    id =  db.Column(db.Integer, primary_key=True)


class Tablet(db.Model, GlyphMixin):
    museum_number = db.Column(db.String(75), nullable=False, unique=True)
    medium_id = db.Column(db.Integer(), db.ForeignKey('medium.id'), nullable=False)
    script_type_id = db.Column(db.Integer(), db.ForeignKey('script_type.id'), nullable=True)
    city_id = db.Column(db.Integer(), db.ForeignKey('city.id'), nullable=True)
    origin_city_id = db.Column(db.Integer(), db.ForeignKey('city.id'), nullable=True)
    publication = db.Column(db.String(200), nullable=True)
    period_id = db.Column(db.Integer(), db.ForeignKey('period.id'), nullable=False)
    from_id = db.Column(db.Integer(), db.ForeignKey('correspondent.id'), nullable=True)
    to_id = db.Column(db.Integer(), db.ForeignKey('correspondent.id'), nullable=True)
    year = db.Column(db.String(10), nullable=True)
    month = db.Column(db.String(10), nullable=True)
    day = db.Column(db.String(10), nullable=True)
    eponym_id = db.Column(db.Integer(), db.ForeignKey('eponym.id'), nullable=True)
    text_vehicle_id = db.Column(db.Integer(), db.ForeignKey('text_vehicle.id'), nullable=True)
    notes = db.Column(db.String(500), nullable=True)
    # relations
    medium = db.relationship("Medium", uselist=False, backref="tablet")
    script_type = db.relationship("Script_Type", uselist=False, backref="tablet")
    city = db.relationship("City",
        primaryjoin="City.id == Tablet.city_id", uselist=False, backref="tablet")
    origin_city = db.relationship("City",
        primaryjoin="City.id == Tablet.origin_city_id", uselist=False, backref="origin_tablet")
    period = db.relationship("Period", uselist=False, backref="tablet")
    sent_from = db.relationship("Correspondent",
        primaryjoin="Correspondent.id == Tablet.from_id", uselist=False, backref="tablet_from")
    sent_to = db.relationship("Correspondent",
        primaryjoin="Correspondent.id == Tablet.to_id", uselist=False, backref="tablet_to")
    eponym = db.relationship("Eponym", uselist=False, backref="tablet")
    text_vehicle = db.relationship("Text_Vehicle", uselist=False, backref="tablet")
    
    def __init__(self, **kwargs):
        """ this will obviously fall over if you forget a required column """
        self.museum_number = kwargs.get("museum_number")
        self.medium = kwargs.get("medium")
        self.script_type = kwargs.get("script_type")
        self.city = kwargs.get("city")
        self.origin_city = kwargs.get("origin_city")
        self.publication = kwargs.get("publication")
        self.period = kwargs.get("period")
        self.sent_from = kwargs.get("sent_from")
        self.sent_to = kwargs.get("sent_to")
        self.year = kwargs.get("year")
        self.month = kwargs.get("month")
        self.day = kwargs.get("day")
        self.eponym = kwargs.get("eponym")
        self.text_vehicle = kwargs.get("text_vehicle")
        self.notes = kwargs.get("notes")


class Non_Ruler_Corresp(db.Model, GlyphMixin):
    """
    This holds correspondents who aren't rulers
    """
    name = db.Column(db.String(100), nullable=False)

    def __init__(self, name):
        self.name = name


class Correspondent(db.Model, GlyphMixin):
    ruler_id = db.Column(
        db.Integer(), db.ForeignKey("ruler.id"), nullable=True)
    non_ruler_id = db.Column(
        db.Integer, db.ForeignKey("non_ruler_corresp.id"), nullable=True)
    # relations
    ruler = db.relationship("Ruler", uselist=False, backref="correspondent")
    non_ruler = db.relationship("Non_Ruler_Corresp", uselist=False, backref="correspondent")

    def __init__(self, ruler=None, non_ruler=None):
        assert (ruler is None) ^ (non_ruler is None)
        if ruler:
            self.ruler = ruler
        if non_ruler:
            self.non_ruler = non_ruler

    @property
    def name(self):
        return self.ruler.name if self.ruler else self.non_ruler.name


class Locality(db.Model, GlyphMixin):
    area = db.Column(db.String(100), nullable=False)
    sub_locality_id = db.Column(
        db.Integer(), db.ForeignKey("sub_locality.id"), nullable=True)
    # relations
    sub_locality = db.relationship("Sub_Locality", uselist=False, backref="locality")

    def __init__(self, area, sub_locality_id=None):
        self.area = area
        if sub_locality_id:
            self.sub_locality_id = sub_locality_id


class Sub_Locality(db.Model, GlyphMixin):
    name = db.Column(db.String(100), nullable=False)
    
    def __init__(self, name):
        self.name = name


class Method(db.Model, GlyphMixin):
    name = db.Column(db.String(50), nullable=False)

    def __init__(self, name):
        self.name = name


class Script_Type(db.Model, GlyphMixin):
    name = db.Column(db.String(50), nullable=False)

    def __init__(self, name):
        self.name = name


class Medium(db.Model, GlyphMixin):
    name = db.Column(db.String(50), nullable=False)

    def __init__(self, name):
        self.name = name


class Genre(db.Model, GlyphMixin):
    name = db.Column(db.String(100), nullable=False)

    def __init__(self, name):
        self.name = name


class Function(db.Model, GlyphMixin):
    name = db.Column(db.String(50), nullable=False)

    def __init__(self, name):
        self.name = name


class Text_Vehicle(db.Model, GlyphMixin):
    name = db.Column(db.String(100), nullable=False)

    def __init__(self, name):
        self.name = name


class Eponym(db.Model, GlyphMixin):
    name = db.Column(db.String(50), nullable=False)
    year = db.Column(db.String(10), nullable=True)

    def __init__(self, name, year=None):
        self.name = name
        if year:
            self.year = year


class Period(db.Model, GlyphMixin):
    name = db.Column(db.String(150), nullable=False)
    sub_period_id = db.Column(
        db.Integer(), db.ForeignKey("sub_period.id"), nullable=True)
    # relations
    sub_period = db.relationship("Sub_Period", uselist=False, backref="period")

    def __init__(self, name, sub_period_id=None):
        self.name = name
        if sub_period_id:
            self.sub_period_id = sub_period_id


class Sub_Period(db.Model, GlyphMixin):
    name = db.Column(db.String(100), nullable=False)

    def __init__(self, name):
        self.name = name


class City(db.Model, GlyphMixin):
    name = db.Column(db.String(100), nullable=False)
    locality_id = db.Column(
        db.Integer(), db.ForeignKey('locality.id'), nullable=True)
    city_site_id = db.Column(
        db.Integer(), db.ForeignKey('city_site.id'), nullable=True)
    # relations
    locality = db.relationship("Locality", uselist=False, backref="city")
    site = db.relationship("City_Site", uselist=False, backref="city")

    def __init__(self, name, locality_id, city_site_id=None):
        self.name = name
        self.locality_id = locality_id
        if city_site_id:
            self.city_site_id = city_site_id


class City_Site(db.Model, GlyphMixin):
    name = db.Column(db.String(100), nullable=False)

    def __init__(self, name):
        self.name = name


class Ruler(db.Model, GlyphMixin):
    name = db.Column(db.String(100), nullable=False)
    rim_ref = db.Column(db.String(30), nullable=True)
    city_id = db.Column(db.Integer(), db.ForeignKey('city.id'), nullable=True)
    start_year = db.Column(db.String(4), nullable=True)
    end_year = db.Column(db.String(4), nullable=True)
    # relations
    city = db.relationship("City", uselist=False, backref="ruler")

    def __init__(self, name, rim_ref=None, city_id=None, start_year=None, end_year=None):
        self.name = name
        if rim_ref:
            self.rim_ref = rim_ref
        if city_id:
            self.city_id = city_id
        if start_year:
            self.start_year = start_year
        if end_year:
            self.end_year = end_year
