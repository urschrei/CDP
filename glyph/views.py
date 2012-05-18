from glyph import app, db
from flask import request, render_template
from models import Test
from forms import RecordForm


@app.route('/', methods=['GET', 'POST'])
def index():
    """ Records """
    form = RecordForm()
    if request.method == 'POST' and form.validate_on_submit():
        record = Test(form.record.data)
        db.session.add(record)
        db.session.commit()
    return render_template('index.jinja', form=form)


@app.route('/records/<int:page>')
def records(page=1):
    page = Test.query.paginate(page, per_page=5)
    return render_template('records.jinja', page=page)
