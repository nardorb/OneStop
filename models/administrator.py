from google.appengine.ext import db

from models.profile import Profile


class Administrator(Profile):
  # Admin details information.
  admin_key = db.IntegerProperty(default=None)
  admin_password = db.StringProperty(default=None)


  def set_admin_key(self, admin_key):
  # hashed_password = webapp2_extras.security.generate_password_hash(password, method='sha1', length=22, pepper=None)
  # TODO: Randomly generate admin code and store copy of code in an admin file.
    return None

  def set_admin_pwd(self, admin_password):
    return None

  def is_editable_by(sef):
    editor = (administrator.is_admin or administrator.is_sys_manager
              or administrator.key() == self.key())