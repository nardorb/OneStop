from google.appengine.ext import db

from models.profile import Profile


class Order(db.Model):

  origin = db.StringProperty(default=None)
  destination = db.StringProperty(default=None)
  passengers = db.StringProperty(default=1)
  comments = db.StringProperty(default=None)
  profile = db.ReferenceProperty(Profile, collection_name='profile')


def get_account(self):
  return self.parent()

def put(self, *args, **kwargs):
    # This is not at the top to prevent circular imports.
    from models.account import Account
    parent = self.parent()
    if not parent or not isinstance(parent, Account):
      raise ValueError(self.EXCEPTION_NO_PARENT)

    return super(Order, self).put(*args, **kwargs)