from google.appengine.ext import db

from models.profile import Profile


class Commuter(Profile):
  tel = db.IntegerProperty(default=None)
  id_number = db.Boolean(default=None)

