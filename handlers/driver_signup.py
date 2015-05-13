from forms.profile import ProfileForm
from handlers import base
from library.auth import login_not_required
from library import messages
from library import constants
from models.account import Account
from models.profile import Profile
from forms.taxi_driver import TaxiDriverForm
from models.taxi_driver import TaxiDriver


class DriverSignupHandler(base.BaseHandler):

  ERROR_MESSAGE = 'Whoops! There was a problem! Sorry about that...'

  @login_not_required
  def driver_signup(self):
    form1 = ProfileForm(self.request.POST)

    if self.request.method == 'POST' and form1.validate():
      # Create the webapp2_extras.auth user.
      model = self.auth.store.user_model
      ok, user = model.create_user(form1.data['email'],
                                   password_raw=form1.data['password'])

      if not ok:
        self.session.add_flash(messages.ERROR_MESSAGE, level='error')
        return self.redirect_to('signup')

      # Ensure that we have a default account setup.
      default_account = Account.all().filter(
          'name = ', constants.PRODUCT_NAME).get()

      if not default_account:
        default_account = Account(name=constants.PRODUCT_NAME)
        default_account.put()

      # Create the profile.
      name = ' '.join([form1.data['first_name'], form1.data['last_name']])
      profile = Profile(parent=default_account,
                        name=name,
                        email=form1.data['email'],
                        tel_number=form1.data['tel_number'],
                        is_driver=True,
                        auth_user_id=user.key.id())
      profile.put()


    form2 = TaxiDriverForm(self.request.POST)

    if self.request.method == 'POST' and form2.validate():

      # Ensure that we have a default account setup.
      default_account = Account.all().filter(
          'name = ', constants.PRODUCT_NAME).get()

      if not default_account:
        default_account = Account(name=constants.PRODUCT_NAME)
        default_account.put()

      if TaxiDriver.get_by_driver_id(form2.data['driver_id']):
        self.session.add_flash(messages.TAXI_DRIVER_EXISTS,
                               level='error')
        return self.render_to_response('taxi_driver/form.haml', {'form': form})

      name = ' '.join((form2.data['first_name'],
                                  form2.data['last_name']))

      taxi_driver = TaxiDriver(parent=default_account,
                               name=name,
                               driver_id=form2.data['driver_id'],
                               email=form2.data['email'],
                               sex=form2.data['sex'],
                               address=form2.data['address'],
                               tel_number=form2.data['tel_number'],
                               parish=form2.data['parish'],
                               dob=form2.data['dob'])
      taxi_driver.put()


      # Automatically log the person in.
      user_id = user.key.id()
      self.auth.get_user_by_token(user_id, user.create_auth_token(user_id))

      self.session.add_flash(messages.PROFILE_CREATE_SUCCESS, level='info')
      return self.redirect_to('home')

    return self.render_to_response('driver-signup.html', {'form': form})
