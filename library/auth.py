def login_not_required(handler_method):
  """Allows someone to *not* be logged in.

  The login_required attribute is inspected by handlers.base.BaseHandlerMeta
  and is used as the flag for whether to wrap a method with login_required
  or not.
  """
  handler_method.login_required = False
  return handler_method


def login_required(handler_method):
  """Requires that this person be logged in."""

  already_wrapped = getattr(handler_method, 'wrapped', False)
  login_required = getattr(handler_method, 'login_required', True)

  # If the method doesn't require a login, or has already been wrapped,
  # just return the original.
  if not login_required or already_wrapped:
    return handler_method

  # This method wraps handlers that require logged-in users.
  def wrapped_handler(self, *args, **kwargs):
    if self.auth.get_user_by_session() and self.get_current_profile():
      return handler_method(self, *args, **kwargs)
    else:
      uri = self.uri_for('login', redirect=self.request.path)
      self.redirect(uri, abort=True)

  # Let others know that this method is already wrapped to avoid wrapping
  # it more than once.
  wrapped_handler.wrapped = True

  return wrapped_handler


class role_required(object):
  def __init__(self, is_admin=None, is_driver=None, is_member=None):
    self.is_admin = is_admin
    self.is_driver = is_driver
    self.is_member = is_member

  def __call__(self, handler_method):
    decorator_self = self

    def wrapped_handler(self, *args, **kwargs):

      if decorator_self.has_permission(self.get_current_profile()):
        return handler_method(self, *args, **kwargs)
      else:
        self.session.add_flash('Invalid permission to view page.',
                               level='error')
        return self.redirect_to('home')
    return wrapped_handler

  def has_permission(self, profile):
    if not profile:
      return False
    if self.is_admin and self.is_admin == profile.is_admin:
      return True
    if self.is_driver and self.is_driver == profile.is_driver:
      return True
    if self.is_member and self.is_member == profile.is_member:
      return True

    return False

admin_required = role_required(is_admin=True)
driver_required = role_required(is_driver=True)
member_required = role_required(is_member=True)
