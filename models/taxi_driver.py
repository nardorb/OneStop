from google.appengine.ext import db


class TaxiDriver(db.Model):
  EXCEPTION_NO_PARENT = "`parent` property must be an `Account` object."

  name = db.StringProperty(default=None)
  email = db.EmailProperty(default=None)
  sex = db.StringProperty(default=None)
  address = db.StringProperty(default=None)
  parish = db.StringProperty(default=None)
  tel_number = db.StringProperty(default=None)
  # years_with_license = db.StringProperty(default=None)
  # road_accidents = db.IntegerProperty(default=None)
  driver_id = db.StringProperty(default=None)
  is_on_duty = db.BooleanProperty(default=False)
  location = db.StringProperty(default=None)
  dob = db.StringProperty(default=None)

  @classmethod
  def get_by_driver_id(cls, driver_id):
    return cls.all().filter('driver_id =', driver_id).get()

  def get_by_location(self, location):
    return None

  def put(self, *args, **kwargs):
    # This is not at the top to prevent circular imports.
    from models.account import Account
    parent = self.parent()
    if not parent or not isinstance(parent, Account):
      raise ValueError(self.EXCEPTION_NO_PARENT)

    return super(TaxiDriver, self).put(*args, **kwargs)