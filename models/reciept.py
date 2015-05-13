from datetime import datetime

from google.appengine.ext import db
import pytz

from models.taxi_driver import TaxiDriver


class Reciept(db.Model):
  EXCEPTION_NO_PARENT = "`parent` property must be a `Profile` object."

  created = db.DateProperty(auto_now_add=True)

  # Basic details
  cost = db.FloatProperty(default=0.00)
  taxi_driver = db.ReferenceProperty(TaxiDriver, collection_name='taxi_driver')
  stub =  db.StringProperty(default=None)

  # @classmethod
  # def get_by_email(cls, email):
  #   return cls.all().filter('email =', email).get()

  def get_profile(self):
    return self.parent()

  def get_current_time(self):
    utc_now = pytz.utc.localize(datetime.utcnow())
    return utc_now.astimezone(self.get_timezone())

  def put(self, *args, **kwargs):
    # This is not at the top to prevent circular imports.
    from models.profile import Profile
    parent = self.parent()
    if not parent or not isinstance(parent, Profile):
      raise ValueError(self.EXCEPTION_NO_PARENT)

    return super(Reciept, self).put(*args, **kwargs)
