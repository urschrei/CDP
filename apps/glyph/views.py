from apps.shared.models import db
from flask import Blueprint, request, render_template
from models import *
from forms import RecordForm

glyph = Blueprint(
    'glyph',
    __name__,
    template_folder='templates'
)


@glyph.route('/', methods=['GET', 'POST'])
def index():
    """ Records """
    form = RecordForm()
    if request.method == 'POST' and form.validate_on_submit():
        record = Test(form.record.data)
        db.session.add(record)
        db.session.commit()
    return render_template('index.jinja', form=form)


@glyph.route(
    '/signs',
    methods=['GET'],
    defaults={'page': 1})
@glyph.route(
    '/tablets/<int:page>',
    methods=['GET'])
def signs(page):
    q = Cdp.query.order_by("sign_ref")
    page = q.paginate(page, per_page=25)
    return render_template('signs.jinja', page=page)


@glyph.route(
    '/sign/<int:cdp_id>',
    methods=['GET'])
def sign(cdp_id):
    signs = Sign.query.filter_by(cdp_id=cdp_id)
    return render_template('sign.jinja', signs=signs)


@glyph.route(
    '/tablet/<int:tablet_id>',
    methods=['GET'])
def tablet(tablet_id):
    tablet = Tablet.query.get_or_404(tablet_id)
    # split Signs into 12-item chunks
    # chunked = list(chunks(tablet.signs, 12))
    chunked = list(chunks(range(36), 12))
    return render_template('tablet.jinja', tablet=tablet, chunks=chunked)


@glyph.route(
    '/tablets',
    methods=['GET'],
    defaults={'page': 1})
@glyph.route(
    '/tablets/<int:page>',
    methods=['GET'])
def tablets(page):
    """
    Show result of restricting records using various criteria
    """
    q = Tablet.query
    if request.args.get("ruler"):
        q = Tablet.query.filter(
            Tablet.rulers.any(Ruler.name == request.args.get("ruler")))
    if request.args.get("medium"):
        q = q.join(Medium).filter(
            Medium.name == request.args.get("medium"))
    if request.args.get("script_type"):
        q = q.join(Script_Type).filter(
            Script_Type.script == request.args.get("script_type"))
    if request.args.get("city"):
        q = q.join(City, Tablet.city_id == City.id).filter(
            City.name == request.args.get("city"))
    if request.args.get("locality"):
        q = q.join(Locality).filter(
            Locality.area == request.args.get("locality"))
    if request.args.get("period"):
        q = q.join(Period).filter(
            Period.name == request.args.get("period"))
    if request.args.get("sub_period"):
        q = q.join(Sub_Period).filter(
            Sub_Period.name == request.args.get("sub_period"))
    if request.args.get("sent_from"):
        q = q.join(Correspondent, Tablet.from_id == Correspondent.id)\
            .filter(Correspondent.name == request.args.get("sent_from"))
    if request.args.get("sent_to"):
        q = q.join(Correspondent, Tablet.to_id == Correspondent.id)\
            .filter(Correspondent.name == request.args.get("sent_to"))
    if request.args.get("year"):
        q = q.join(Year).filter(
            Year.year == request.args.get("year"))
    if request.args.get("eponym"):
        q = q.join(Year).join(Eponym).filter(
            Eponym.name == request.args.get("eponym"))
    if request.args.get("text_vehicle"):
        q = q.join(Text_Vehicle).filter(
            Text_Vehicle.name == request.args.get("text_vehicle"))
    if request.args.get("language"):
        q = q.join(Language).filter(
            Language.name == request.args.get("language"))
    if request.args.get("method"):
        q = q.join(Method).filter(
            Method.name == request.args.get("method"))
    if request.args.get("genre"):
        q = q.join(Genre).filter(
            Genre.name == request.args.get("genre"))
    if request.args.get("function"):
        q = q.join(Function).filter(
            Function.name == request.args.get("function"))
    if request.args.get("dynasty"):
        q = q.join(Dynasty).filter(
            Dynasty.name == request.args.get("dynasty"))
    page = q.paginate(page, per_page=25)
    return render_template('tablets.jinja', page=page)


# utilities
def chunks(l, n):
    """ Yield successive n-sized chunks from l.
    """
    for i in xrange(0, len(l), n):
        yield l[i:i + n]
