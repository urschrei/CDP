from flask_wtf import Form
from wtforms import (
    TextAreaField,
    StringField,
    validators
)


class RecordForm(Form):
    record = TextAreaField(
        u"Record Text",
        [validators.DataRequired(
            u"Please enter some text."),
            validators.length(
                max=50,
                message=u"Please use 50 characters or less")])


class SearchForm(Form):
    search = StringField('Search', validators=[validators.DataRequired()])
