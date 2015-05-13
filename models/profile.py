from datetime import datetime
import uuid

from google.appengine.ext import db
import pytz
from webapp2_extras import auth


class Profile(db.Model):
  default_TIMEZONE = 'America/Jamaica'
  EXCEPTION_NO_PARENT = "`parent` property must be an `Account` object."

  # Tie back to webapp2 auth
  auth_user_id = db.IntegerProperty()

  # Administrative details
  created = db.DateProperty(auto_now_add=True)
  is_admin = db.BooleanProperty(default=False)
  is_driver = db.BooleanProperty(default=False)
  is_member = db.BooleanProperty(default=False)

  # Basic details
  name = db.StringProperty(default=None)
  email = db.EmailProperty(default=None)
  tel_number = db.StringProperty(default=None)
  credit = db.FloatProperty(default=0.00)
  timezone = db.StringProperty()
  # activated = db.BooleanProperty(default=False)
  # activation_key = db.StringProperty()

  @classmethod
  def get_by_email(cls, email):
    return cls.all().filter('email =', email).get()

  # @classmethod
  # def get_by_activation_key(cls, activation_key):
  #   return cls.all().filter('activation_key =', activation_key).get()

  @classmethod
  def get_by_auth_user_id(cls, id):
    return cls.all().filter('auth_user_id =', id).get()

  def get_account(self):
    return self.parent()

  def get_auth_user(self):
    return auth.get_auth().store.user_model.get_by_id(self.auth_user_id)

  def get_current_time(self):
    utc_now = pytz.utc.localize(datetime.utcnow())
    return utc_now.astimezone(self.get_timezone())

  def get_timezone(self):
    return pytz.timezone(self.timezone or self.default_TIMEZONE)

  def is_editable_by(self, profile):
    same_account = self.get_account().key() == profile.get_account().key()
    can_edit = (profile.is_admin
                or profile.key() == self.key())

    return same_account and can_edit

  def put(self, *args, **kwargs):
    # This is not at the top to prevent circular imports.
    from models.account import Account
    parent = self.parent()
    if not parent or not isinstance(parent, Account):
      raise ValueError(self.EXCEPTION_NO_PARENT)

    return super(Profile, self).put(*args, **kwargs)
