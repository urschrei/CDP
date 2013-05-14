import random
import string
from app import db
from models import Test


def generate_random(size=7):
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for x in xrange(size))


entries = [generate_random() for each in xrange(50)]
tests = [Test(entry) for entry in entries]
db.session.add_all(tests)
db.session.commit()
