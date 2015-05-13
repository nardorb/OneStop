from webapp2_extras import security

from forms.profile_activation import ProfileActivationForm
from handlers import base
from library.auth import login_not_required
from library import messages
from models.profile import Profile


class ProfileHandler(base.BaseHandler):

  @login_not_required
  def activate(self):
    # k is used in emails
    # activation_key is the form name
    key = self.request.get('k')
    profile = Profile.get_by_activation_key(key)

    if not profile or profile.activated:
      self.session.add_flash(messages.PROFILE_ACTIVATION_NOT_FOUND,
                             level='error')
      self.redirect_to('home')

    form = ProfileActivationForm(self.request.POST, obj=profile)
    form.activation_key = key

    if self.request.method == 'POST' and form.validate():
      # Create the webapp2_extras.auth user.
      model = self.auth.store.user_model
      ok, user = model.create_user(profile.email,
                                   password_raw=form.data['password'])

      if not ok:
        self.session.add_flash(messages.PROFILE_ACTIVATION_ERROR,
                               level='error')
        return self.redirect_to('profile.activate', k=key)

      # Setup profile, create authentication token and activate
      profile.name = ' '.join([form.data['first_name'],
                               form.data['last_name']])

      # Set as activated (since they've confirmed their e-mail).
      profile.activated = True
      profile.activation_key = None
      profile.auth_user_id = user.key.id()
      profile.put()

      # Change the password for the auth_user.
      user = self.auth.store.user_model.get_by_id(profile.auth_user_id)
      user.password = security.generate_password_hash(form.data['password'],
                                                      length=12)
      user.put()

      # Log the user in.
      user_id = user.key.id()
      self.auth._user = None
      self.auth.get_user_by_token(user_id, user.create_auth_token(user_id))

      # Redirect to the dashboard.
      self.session.add_flash(messages.PROFILE_ACTIVATION_SUCCESS)
      return self.redirect_to('home')

    return self.render_to_response('activate.haml',
                                   {'profile': profile, 'form': form})

  def view(self):
    return
