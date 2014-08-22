from flask import current_app
from apps.shared.models import db, GlyphMixin

from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import backref



class Tablet(db.Model, GlyphMixin):
    timestamp = db.Column(
        db.DateTime(timezone=True),
        default=db.func.now(),
        nullable=False)
    museum_number = db.Column(
        db.String(75),
        nullable=False,
        unique=True)
    medium_id = db.Column(
        db.Integer(),
        db.ForeignKey('medium.id'),
        nullable=False)
    script_type_id = db.Column(
        db.Integer(),
        db.ForeignKey('script_type.id'),
        nullable=True)
    city_id = db.Column(
        db.Integer(),
        db.ForeignKey('city.id'),
        nullable=True)
    city_site_id = db.Column(
        db.Integer(),
        db.ForeignKey('city_site.id'),
        nullable=True)
    origin_city_id = db.Column(
        db.Integer(),
        db.ForeignKey('city.id'),
        nullable=True)
    publication = db.Column(
        db.String(200),
        nullable=True)
    period_id = db.Column(
        db.Integer(),
        db.ForeignKey('period.id'),
        nullable=False)
    sub_period_id = db.Column(
        db.Integer(),
        db.ForeignKey('sub_period.id'),
        nullable=True)
    from_id = db.Column(
        db.Integer(),
        db.ForeignKey('correspondent.id'),
        nullable=True)
    to_id = db.Column(
        db.Integer(),
        db.ForeignKey('correspondent.id'),
        nullable=True)
    language_id = db.Column(
        db.Integer(),
        db.ForeignKey('language.id'),
        nullable=True)
    eponym_id = db.Column(
        db.Integer(),
        db.ForeignKey("eponym.id"),
        nullable=True)
    # absolute year / month / day
    year_id = db.Column(
        db.Integer(),
        db.ForeignKey('year.id'),
        nullable=True)
    absolute_month = db.Column(
        db.String(10),
        nullable=True)
    absolute_day = db.Column(
        db.String(10),
        nullable=True)
    # ancient year / month / day
    ancient_year = db.Column(
        db.String(10),
        nullable=True)
    ancient_month = db.Column(
        db.String(10),
        nullable=True)
    ancient_day = db.Column(
        db.String(10),
        nullable=True)
    dynasty_id = db.Column(
        db.Integer(),
        db.ForeignKey('dynasty.id'),
        nullable=True)
    text_vehicle_id = db.Column(
        db.Integer(),
        db.ForeignKey('text_vehicle.id'),
        nullable=True)
    locality_id = db.Column(
        db.Integer(),
        db.ForeignKey('locality.id'),
        nullable=True)
    sub_locality_id = db.Column(
        db.Integer(),
        db.ForeignKey('sub_locality.id'),
        nullable=True)
    notes = db.Column(
        db.String(500),
        nullable=True)
    method_id = db.Column(
        db.Integer(),
        db.ForeignKey('method.id'),
        nullable=True)
    genre_id = db.Column(
        db.Integer(),
        db.ForeignKey('genre.id'),
        nullable=True)
    function_id = db.Column(
        db.Integer(),
        db.ForeignKey('function.id'),
        nullable=True)
    reign_id = db.Column(
        db.Integer(),
        db.ForeignKey("reign.id"),
        nullable=True)
    author_id = db.Column(
        db.Integer(),
        db.ForeignKey('author.id'),
        nullable=True)
    # association proxy for rulers
    rulers = association_proxy(
        'tablet_ruler',
        'ruler',
        creator=lambda rul: Ruler_Tablet(ruler=rul))
    # association proxy for sent_to correspondents
    sent_to = association_proxy(
        'tablet_correspondents',
        'correspondent',
        creator=lambda cor: Tablet_Correspondent(correspondent=cor))
    # relations
    author = db.relationship(
        "Author",
        backref="tablets")
    eponym = db.relationship(
        "Eponym",
        backref="tablets")
    year = db.relationship(
        "Year",
        backref="tablets")
    medium = db.relationship(
        "Medium",
        backref="tablets")
    script_type = db.relationship(
        "Script_Type",
        backref="tablets")
    locality = db.relationship(
        "Locality",
        backref="tablets")
    sub_locality = db.relationship(
        "Sub_Locality",
        backref="tablets")
    city = db.relationship(
        "City",
        primaryjoin="City.id == Tablet.city_id",
        backref="tablets")
    city_site = db.relationship(
        "City_Site",
        primaryjoin="City_Site.id == Tablet.city_site_id",
        backref="tablets")
    origin_city = db.relationship(
        "City",
        primaryjoin="City.id == Tablet.origin_city_id",
        backref="origin_tablets")
    period = db.relationship(
        "Period",
        backref="tablets")
    sub_period = db.relationship(
        "Sub_Period",
        backref="tablets")
    sent_from = db.relationship(
        "Correspondent",
        primaryjoin="Correspondent.id == Tablet.from_id",
        backref="tablets_from")
    text_vehicle = db.relationship(
        "Text_Vehicle",
        backref="tablets")
    language = db.relationship(
        "Language",
        backref="tablets")
    method = db.relationship(
        "Method",
        backref="tablets")
    genre = db.relationship(
        "Genre",
        backref="tablets")
    function = db.relationship(
        "Function",
        backref="tablets")
    dynasty = db.relationship(
        "Dynasty",
        backref="tablets")
    reign = db.relationship(
        "Reign",
        backref="tablets")
    instances = db.relationship("Instance", backref="tablet")

    def __init__(self, **kwargs):
        """
        this will obviously fall over if you forget a required column:
        medium and period are both required
        """
        self.museum_number = kwargs.get("museum_number")
        self.medium = kwargs.get("medium")
        self.script_type = kwargs.get("script_type")
        self.locality = kwargs.get("locality")
        self.sub_locality = kwargs.get("sub_locality")
        self.city = kwargs.get("city")
        self.city_site = kwargs.get("city_site")
        self.origin_city = kwargs.get("origin_city")
        self.publication = kwargs.get("publication")
        self.period = kwargs.get("period")
        self.sub_period = kwargs.get("sub_period")
        self.sent_from = kwargs.get("sent_from")
        self.sent_to = kwargs.get("sent_to")
        # absolute year
        self.year = kwargs.get("year")
        self.absolute_month = kwargs.get("absolute_month")
        self.absolute_day = kwargs.get("absolute_day")
        self.ancient_year = kwargs.get("ancient_year")
        self.ancient_month = kwargs.get("ancient_month")
        self.ancient_day = kwargs.get("ancient_day")
        self.text_vehicle = kwargs.get("text_vehicle")
        self.notes = kwargs.get("notes")
        self.language = kwargs.get("language")
        self.method = kwargs.get("method")
        self.genre = kwargs.get("genre")
        self.function = kwargs.get("function")
        self.dynasty = kwargs.get("dynasty")
        self.reign = kwargs.get("reign")
        self.eponym = kwargs.get("eponym")
        self.author = kwargs.get("author")

    @property
    def absolute_year(self):
        return self.year.year


class Non_Ruler_Corresp(db.Model, GlyphMixin):
    """
    This holds correspondents who aren't rulers
    """
    name = db.Column(db.String(100), nullable=False, unique=True)

    def __init__(self, name):
        self.name = name


class Author(db.Model, GlyphMixin):
    """
    Tablet authors
    """
    name = db.Column(db.String(75), nullable=False, unique=True)

    def __init__(self, name):
        self.name = name


class Correspondent(db.Model, GlyphMixin):
    """
    A correspondent can be a ruler or a non-ruler
    Note use of @property to return the correct value
    """
    ruler_id = db.Column(
        db.Integer(), db.ForeignKey("ruler.id"), nullable=True)
    non_ruler_id = db.Column(
        db.Integer, db.ForeignKey("non_ruler_corresp.id"), nullable=True)
    # relations
    ruler = db.relationship(
        "Ruler",
        primaryjoin="Ruler.id == Correspondent.ruler_id",
        uselist=False, backref="correspondent")
    non_ruler = db.relationship(
        "Non_Ruler_Corresp",
        primaryjoin="Non_Ruler_Corresp.id == Correspondent.non_ruler_id",
        uselist=False, backref="correspondent")
    # association proxy for tablets
    tablets = association_proxy(
        'correspondent_tablets',
        'tablet',
        creator=lambda tab: Tablet_Correspondent(tablet=tab))

    def __init__(self, ruler=None, non_ruler=None, tablets=None):
        assert (ruler is None) ^ (non_ruler is None)
        if ruler:
            self.ruler = ruler
        if non_ruler:
            self.non_ruler = non_ruler
        self.tablets = tablets

    @property
    def name(self):
        return self.ruler.name if self.ruler else self.non_ruler.name


class Locality(db.Model, GlyphMixin):
    area = db.Column(db.String(100), nullable=False, unique=True)
    # relations
    sub_localities = db.relationship("Sub_Locality", backref="locality")
    cities = db.relationship("City", backref="locality")

    def __init__(self, area, sub_localities=None):
        self.area = area
        if sub_localities:
            self.sub_localities = sub_localities


class Sub_Locality(db.Model, GlyphMixin):
    name = db.Column(db.String(100), nullable=False, unique=True)
    locality_id = db.Column(
        db.Integer(), db.ForeignKey("locality.id"), nullable=True)

    def __init__(self, name, locality):
        self.name = name
        self.locality = locality


class City(db.Model, GlyphMixin):
    name = db.Column(db.String(100), nullable=False, unique=True)
    locality_id = db.Column(
        db.Integer(), db.ForeignKey('locality.id'), nullable=True)
    # relations
    sites = db.relationship("City_Site", backref="city")
    # association proxy for ruler / city
    # rulers = association_proxy('city_ruler', 'ruler')

    def __init__(self, name, locality=None, sites=None):
        self.name = name
        if locality:
            self.locality = locality
        if sites:
            self.sites = sites


class City_Site(db.Model, GlyphMixin):
    name = db.Column(db.String(100), nullable=False, unique=True)
    city_id = db.Column(
        db.Integer(), db.ForeignKey("city.id"), nullable=False)

    def __init__(self, name, city):
        self.name = name
        self.city = city


class Method(db.Model, GlyphMixin):
    name = db.Column(db.String(50), nullable=False, unique=True)

    def __init__(self, name):
        self.name = name


class Script_Type(db.Model, GlyphMixin):
    script = db.Column(db.String(50), nullable=False, unique=True)

    def __init__(self, script):
        self.script = script


class Year(db.Model, GlyphMixin):
    year = db.Column(db.String(14), nullable=False, unique=True)
    eponym_id = db.Column(
        db.Integer(), db.ForeignKey("eponym.id"), nullable=True)
    # relations
    eponym = db.relationship("Eponym", uselist=False, backref="year")

    def __init__(self, year, eponym=None):
        self.year = year
        if eponym:
            self.eponym = eponym


class Medium(db.Model, GlyphMixin):
    name = db.Column(db.String(50), nullable=False, unique=True)

    def __init__(self, name):
        self.name = name


class Genre(db.Model, GlyphMixin):
    name = db.Column(db.String(100), nullable=False, unique=True)

    def __init__(self, name):
        self.name = name


class Language(db.Model, GlyphMixin):
    name = db.Column(db.String(100), nullable=False, unique=True)

    # association proxies
    instances = association_proxy(
        'language_instances',
        'instance',
        creator=lambda inst: Instance_Language(instance=inst))

    def __init__(self, name, instances=None):
        self.name = name


class Text_Vehicle(db.Model, GlyphMixin):
    name = db.Column(db.String(100), nullable=False, unique=True)
    bm_catalogue = db.Column(db.String(100), nullable=True)
    cdli = db.Column(db.String(100), nullable=True)

    def __init__(self, name, bm_catalogue=None, cdli=None):
        self.name = name
        if bm_catalogue:
            self.bm_catalogue = bm_catalogue
        if cdli:
            self.cdli = cdli


class Eponym(db.Model, GlyphMixin):
    """
    Like 'Year of Glad', but for rulers
    """
    name = db.Column(db.String(50), nullable=False, unique=True)

    def __init__(self, name, year=None):
        self.name = name


class Period(db.Model, GlyphMixin):
    name = db.Column(db.String(150), nullable=False, unique=True)
    # should these be links to year?
    from_date = db.Column(db.String(50), nullable=False)
    to_date = db.Column(db.String(50), nullable=False)
    # relations
    sub_periods = db.relationship("Sub_Period", backref="period")

    def __init__(self, name, sub_period=None):
        self.name = name
        if sub_period:
            self.sub_period = sub_period


class Sub_Period(db.Model, GlyphMixin):
    name = db.Column(db.String(100), nullable=False, unique=True)
    period_id = db.Column(
        db.Integer(), db.ForeignKey("period.id"), nullable=False)
    # relations
    # AP which gives us all dynasties
    dynasties = association_proxy(
        'subperiod_dynasty',
        'dynasty',
        creator=lambda dyn: Subperiod_Dynasty(dynasty=dyn))

    def __init__(self, name, period):
        self.name = name
        self.period = period


class Ruler(db.Model, GlyphMixin):
    name = db.Column(db.String(100), nullable=False, unique=True)
    # relations
    reigns = db.relationship("Reign", backref="ruler")
    # association proxy for tablets
    tablets = association_proxy(
        'ruler_tablet',
        'tablet',
        creator=lambda tab: Ruler_Tablet(tablet=tab))

    def __init__(self, name, reigns=None):
        self.name = name
        if reigns:
            self.reigns = reigns


class Dynasty(db.Model, GlyphMixin):
    name = db.Column(db.String(100), nullable=False, unique=True)
    # AP which gives us all sub-periods
    sub_periods = association_proxy(
        'dynasty_subperiod',
        'sub_period',
        creator=lambda sub: Subperiod_Dynasty(sub_period=sub))

    def __init__(self, name):
        self.name = name


class Reign(db.Model, GlyphMixin):
    """
    Rulers have reigns. Sometimes, more than one
    """
    ruler_id = db.Column(
        "ruler_id",
        db.Integer(),
        db.ForeignKey("ruler.id"),
        nullable=False)
    rim_ref = db.Column(
        "rim_ref",
        db.String(50),
        nullable=False)
    city_id = db.Column(
        "city_id",
        db.Integer(),
        db.ForeignKey("city.id"),
        nullable=True)
    start_date = db.Column(
        "start_date",
        db.Integer(),
        db.ForeignKey("year.id"),
        nullable=True)
    end_date = db.Column(
        "end_date",
        db.Integer(),
        db.ForeignKey("year.id"),
        nullable=True)
    dynasty_id = db.Column(
        "dynasty_id",
        db.Integer(),
        db.ForeignKey("dynasty.id"),
        nullable=True)
    period_id = db.Column(
        "period_id",
        db.Integer(),
        db.ForeignKey("period.id"),
        nullable=False)
    sub_period_id = db.Column(
        "sub_period_id",
        db.Integer,
        db.ForeignKey("sub_period.id"),
        nullable=True)

    # relations
    city = db.relationship(
        "City",
        backref="reigns")
    start_year = db.relationship(
        "Year",
        primaryjoin="Year.id == Reign.start_date",
        backref="reign_start_years")
    end_year = db.relationship(
        "Year",
        primaryjoin="Year.id == Reign.end_date",
        backref="reign_end_years")
    dynasty = db.relationship(
        "Dynasty",
        backref="reigns")
    period = db.relationship(
        "Period",
        backref="reigns")
    sub_period = db.relationship(
        "Sub_Period",
        backref="reigns")

    def __init__(
        self, rim_ref, period, city=None, start_year=None,
        end_year=None, sub_period=None, dynasty=None):

        self.rim_ref = rim_ref
        self.period = period
        self.start_year = start_year
        self.end_year = end_year
        self.sub_period = sub_period
        self.city = city
        self.dynasty = dynasty


class Ruler_Tablet(db.Model):
    """
    Association object for rulers and tablets
    """
    __tablename__ = "ruler_tablet"
    ruler_id = db.Column(
        "ruler_id",
        db.Integer(),
        db.ForeignKey("ruler.id"),
        primary_key=True)
    tablet_id = db.Column(
        "tablet_id",
        db.Integer(),
        db.ForeignKey("tablet.id"),
        primary_key=True)
    # relations
    ruler = db.relationship(
        "Ruler",
        backref="ruler_tablet",
        cascade="all")
    tablet = db.relationship(
        "Tablet",
        backref="tablet_ruler",
        cascade="all")

    def __init__(self, ruler=None, tablet=None):
        self.ruler = ruler
        self.tablet = tablet


class Tablet_Correspondent(db.Model):
    """
    Association object for Tablets and correspondents
    This allows many tablets to have many correspondents in the SENT_TO field
    """
    __tablename__ = "tablet_correspondent"
    tablet_id = db.Column(
        "tablet_id",
        db.Integer(),
        db.ForeignKey("tablet.id"),
        primary_key=True)
    correspondent_id = db.Column(
        "correspondent_id",
        db.Integer(),
        db.ForeignKey("correspondent.id"),
        primary_key=True)
    # relations
    tablet = db.relationship(
        "Tablet",
        backref="tablet_correspondents",
        cascade="all, delete-orphan",
        single_parent=True)
    correspondent = db.relationship(
        "Correspondent",
        backref="correspondent_tablets",
        cascade="all, delete-orphan",
        single_parent=True)

    def __init__(self, tablet=None, correspondent=None):
        self.tablet = tablet
        self.correspondent = correspondent


class Subperiod_Dynasty(db.Model):
    """
    Association object for subperiod and dynasty
    """
    __tablename__ = "subperiod_dynasty"
    subperiod_id = db.Column(
        "subperiod_id",
        db.Integer(),
        db.ForeignKey("sub_period.id"),
        primary_key=True)
    dynasty_id = db.Column(
        "dynasty_id",
        db.Integer(),
        db.ForeignKey("dynasty.id"),
        primary_key=True)
    # relations
    sub_period = db.relationship(
        "Sub_Period",
        backref="subperiod_dynasty",
        cascade="all, delete-orphan",
        single_parent=True)
    dynasty = db.relationship(
        "Dynasty",
        backref="dynasty_subperiod",
        cascade="all, delete-orphan",
        single_parent=True)

    def __init__(self, sub_period=None, dynasty=None):
        self.sub_period = sub_period
        self.dynasty = dynasty


# these are sign-related tables


class Sign(db.Model, GlyphMixin):
    """ CDP Sign references """
    sign_ref = db.Column(
        db.String(150),
        nullable=False,
        unique=True,
        index=True)

    instances = db.relationship("Instance", backref="sign")
    cdp = db.relationship(
        "Cdp",
        backref=backref("sign"),
        cascade="all, delete-orphan",
        primaryjoin="Sign.id == Cdp.sign_id")

    def __repr__(self):
        return "<Sign: %s>" % self.sign_ref


class Description(db.Model, GlyphMixin):
    """ CDP Sign descriptions """
    sign_ref = db.Column(
        db.String(150),
        nullable=False,
        unique=True,
        index=True)

    cdp = db.relationship(
        "Cdp",
        backref=backref("description"),
        cascade="all, delete-orphan",
        primaryjoin="Description.id == Cdp.description_id")

    def __repr__(self):
        return "<Description: %s>" % self.sign_ref


class Oracc(db.Model, GlyphMixin):
    """ CDP Oracc references """
    sign_ref = db.Column(
        db.String(150),
        nullable=False,
        unique=True,
        index=True)

    cdp = db.relationship(
        "Cdp",
        backref=backref("oracc"),
        cascade="all, delete-orphan",
        primaryjoin="Oracc.id == Cdp.oracc_id")

    def __repr__(self):
        return "<Oracc: %s>" % self.sign_ref


class Cdli(db.Model, GlyphMixin):
    """ CDP CDLI Archaic references """
    sign_ref = db.Column(
        db.String(150),
        nullable=False,
        unique=True,
        index=True)

    cdp = db.relationship(
        "Cdp",
        backref=backref('cdli'),
        cascade="all, delete-orphan",
        primaryjoin="Cdli.id == Cdp.cdli_id")

    def __repr__(self):
        return "<CDLI Archaic: %s>" % self.sign_ref


class Cdp(db.Model, GlyphMixin):
    """
    Sign identification
    """
    sign_id = db.Column(
        "sign_id",
        db.Integer(),
        db.ForeignKey("sign.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False)
    description_id = db.Column(
        "description_id",
        db.Integer(),
        db.ForeignKey("description.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=True)
    oracc_id = db.Column(
        "oracc_id",
        db.Integer(),
        db.ForeignKey("oracc.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=True)
    cdli_id = db.Column(
        "cdli_id",
        db.Integer(),
        db.ForeignKey("cdli.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=True)
    # backrefs for fk relations always go on the 'one' side of one-to-many
    form_name = db.Column(
        db.String(5),
        nullable=True,
        unique=False)
    variant_name = db.Column(
        db.String(5),
        nullable=True,
        unique=False)
    form_description = db.Column(
        db.String(50),
        nullable=True,
        unique=False)
    notes = db.Column(
        db.String(50),
        nullable=True,
        unique=False)
    # signlist columns
    MesZL = db.Column(
        db.String(50),
        nullable=True,
        unique=False)
    ELLes = db.Column(
        db.String(50),
        nullable=True,
        unique=False)
    ZATU = db.Column(
        db.String(50),
        nullable=True,
        unique=False)
    LAK = db.Column(
        db.String(50),
        nullable=True,
        unique=False)
    UET_2 = db.Column(
        db.String(50),
        nullable=True,
        unique=False)
    ARM_XV = db.Column(
        db.String(50),
        nullable=True,
        unique=False)
    Hinke = db.Column(
        db.String(50),
        nullable=True,
        unique=False)
    Clay_BE_A_14 = db.Column(
        db.String(50),
        nullable=True,
        unique=False)
    Koenig_AfO_Bei_16 = db.Column(
        db.String(50),
        nullable=True,
        unique=False)
    Ranke_BE_A_61 = db.Column(
        db.String(50),
        nullable=True,
        unique=False)
    Schroeder_VS_12 = db.Column(
        db.String(50),
        nullable=True,
        unique=False)
    Clay_BE_A_10 = db.Column(
        db.String(50),
        nullable=True,
        unique=False)
    RSP = db.Column(
        db.String(50),
        nullable=True,
        unique=False)
    Emar = db.Column(
        db.String(50),
        nullable=True,
        unique=False)
    Schroder_VS_15 = db.Column(
        db.String(50),
        nullable=True,
        unique=False)
    HZL = db.Column(
        db.String(50),
        nullable=True,
        unique=False)
    HA = db.Column(
        db.String(50),
        nullable=True,
        unique=False)
    aBZL = db.Column(
        db.String(50),
        nullable=True,
        unique=False)
    REC = db.Column(
        db.String(50),
        nullable=True,
        unique=False)
    Labat = db.Column(
        db.String(50),
        nullable=True,
        unique=False)
    KWU = db.Column(
        db.String(50),
        nullable=True,
        unique=False)
    Fossey_pp = db.Column(
        db.String(50),
        nullable=True,
        unique=False)

    def __repr__(self):
        return "<CDP Entry for Sign '%s'>" % (self.sign.sign_ref)


class Function(db.Model, GlyphMixin):
    """
    Instance surface
    """
    name = db.Column(
        db.String(50),
        nullable=False,
        unique=True)

    def __init__(self, name):
        self.name = name


class Surface(db.Model, GlyphMixin):
    """
    Instance surface
    """
    name = db.Column(
        db.String(50),
        nullable=False,
        unique=True)

    def __init__(self, name):
        self.name = name


class Column(db.Model, GlyphMixin):
    """
    Instance column
    """
    number = db.Column(
        db.String(5),
        nullable=False,
        unique=True)

    def __init__(self, number):
        self.number = number


class Line(db.Model, GlyphMixin):
    """
    Instance line
    """
    number = db.Column(
        db.String(5),
        nullable=False,
        unique=True)

    def __init__(self, number):
        self.number = number


class Iteration(db.Model, GlyphMixin):
    """
    Instance iterations
    """
    number = db.Column(
        db.String(5),
        nullable=False,
        unique=True)

    def __init__(self, number):
        self.number = number


class Instance(db.Model, GlyphMixin):
    """
    Instances of signs
    """
    tablet_id = db.Column(
        db.Integer(),
        db.ForeignKey("tablet.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False)
    sign_id = db.Column(
        db.Integer(),
        db.ForeignKey("sign.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False)
    surface_id = db.Column(
        db.Integer(),
        db.ForeignKey("surface.id"),
        nullable=True)
    column_id = db.Column(
        db.Integer(),
        db.ForeignKey("column.id"),
        nullable=True)
    line_id = db.Column(
        db.Integer(),
        db.ForeignKey("line.id"),
        nullable=True)
    function_id = db.Column(
        db.Integer(),
        db.ForeignKey("function.id"),
        nullable=True)
    iteration_id = db.Column(
        db.Integer(),
        db.ForeignKey("iteration.id"),
        nullable=True)
    notes = db.Column(
        db.String(250),
        nullable=True,
        unique=False)
    jjt_notes = db.Column(
        db.String(250),
        nullable=True,
        unique=False)
    filename = db.Column(
        db.String(50),
        nullable=False,
        unique=True)

    # relations
    surface = db.relationship("Surface", backref="instances")
    column = db.relationship("Column", backref="instances")
    line = db.relationship("Line", backref="instances")
    function = db.relationship("Function", backref="instances")
    iteration = db.relationship("Iteration", backref="instances")

    # association proxies
    languages = association_proxy(
        'instance_languages',
        'language',
        creator=lambda lang: Instance_Language(language=lang))

    def __init__(
        self, sign, surface=None, column=None, line=None,
        function=None, iteration=None, notes=None, filename=None,
        languages=None, tablet=None, jjt_notes=None):

        self.sign = sign
        self.surface = surface
        self.column = column
        self.line = line
        self.function = function
        self.iteration = iteration
        self.notes = notes
        self.filename = filename
        self.tablet = tablet
        self.jjt_notes = jjt_notes


class Instance_Language(db.Model):
    """
    Association object for Instances and Languages
    """
    __tablename__ = "instance_language"
    instance_id = db.Column(
        "instance_id",
        db.Integer(),
        db.ForeignKey("instance.id"),
        primary_key=True)
    language_id = db.Column(
        "language_id",
        db.Integer(),
        db.ForeignKey("language.id"),
        primary_key=True)
    # relations
    instance = db.relationship(
        "Instance",
        backref="instance_languages",
        cascade="all")
    language = db.relationship(
        "Language",
        backref="language_instances",
        cascade="all")

    def __init__(self, instance=None, language=None):
        self.instance = instance
        self.language = language
