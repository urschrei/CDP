from glyph import db


class Test(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text_field = db.Column(db.Text, nullable=False)

    def __init__(self, text_field):
        self.text_field = text_field
