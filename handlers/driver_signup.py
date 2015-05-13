from handlers import base
from library.auth import login_not_required
from library import messages
from library import constants
from models.account import Account
from models.profile import Profile
from models.taxi_driver import TaxiDriver
from forms.taxi_driver import TaxiDriverForm


class DriverSignupHandler(base.BaseHandler):

  ERROR_MESSAGE = 'Whoops! There was a problem! Sorry about that...'

  @login_not_required
  def driver_signup(self):
    form = TaxiDriverForm(self.request.POST)

    if self.request.method == 'POST' and form.validate():
      # Create the webapp2_extras.auth user.
      model = self.auth.store.user_model
      ok, user = model.create_user(form.data['email'],
                                   password_raw=form.data['password'])

      if not ok:
        self.session.add_flash(messages.ERROR_MESSAGE, level='error')
        return self.redirect_to('driver-signup')

      # Ensure that we have a default account setup.
      default_account = Account.all().filter(
          'name = ', constants.PRODUCT_NAME).get()

      if not default_account:
        default_account = Account(name=constants.PRODUCT_NAME)
        default_account.put()

      # Create the profile.
      name = ' '.join([form.data['first_name'], form.data['last_name']])
      email = form.data['email']
      tel_num = form.data['tel_number']

      profile = Profile(parent=default_account,
                        name=name,
                        email=email,
                        tel_number=tel_num,
                        is_driver=True,
                        auth_user_id=user.key.id())
      profile.put()

      # Automatically log the person in.
      user_id = user.key.id()
      self.auth.get_user_by_token(user_id, user.create_auth_token(user_id))

      self.session.add_flash(messages.PROFILE_CREATE_SUCCESS, level='info')
      return self.redirect_to('home')

    self.session.add_flash(messages.PROFILE_CREATE_ERROR, level='error')
    return self.render_to_response('driver-signup.html', {'form': form})
