from google.appengine.ext import db
from models.taxi_driver import TaxiDriver


class Taxi(db.Model):
  license_plate = db.StringProperty(default=None)
  is_operational = db.BooleanProperty(default=False)

  # Vehicle description
  make = db.StringProperty(default=None)
  model = db.StringProperty(default=None)
  vehicle_type = db.StringProperty(default="Sedan")
  color = db.StringProperty(default=None)

  taxi_driver = db.ReferenceProperty(TaxiDriver, collection_name='taxi_driver')


  @classmethod
  def get_by_license_plate(cls, license_plate):
    return cls.all().filter('license_plate =', license_plate).get()