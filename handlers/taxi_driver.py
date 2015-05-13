from forms.taxi_driver import TaxiDriverForm
from handlers import base
from library import messages
from library.auth import role_required
from library import constants
from models.taxi_driver import TaxiDriver
from models.account import Account


class TaxiDriverHandler(base.BaseHandler):

  @role_required(is_admin=True)
  def create(self):
    form = TaxiDriverForm(self.request.POST)

    if self.request.method == 'POST' and form.validate():

      # Ensure that we have a default account setup.
      default_account = Account.all().filter(
          'name = ', constants.PRODUCT_NAME).get()

      if not default_account:
        default_account = Account(name=constants.PRODUCT_NAME)
        default_account.put()

      if TaxiDriver.get_by_driver_id(form.data['driver_id']):
        self.session.add_flash(messages.TAXI_DRIVER_EXISTS,
                               level='error')
        return self.render_to_response('taxi_driver/form.haml', {'form': form})

      name = ' '.join((form.data['first_name'],
                                  form.data['last_name']))

      taxi_driver = TaxiDriver(parent=default_account,
                               name=name,
                               driver_id=form.data['driver_id'],
                               email=form.data['email'],
                               sex=form.data['sex'],
                               address=form.data['address'],
                               tel_number=form.data['tel_number'],
                               parish=form.data['parish'],
                               dob=form.data['dob'])
      taxi_driver.put()

      self.session.add_flash(messages.TAXI_DRIVER_CREATE_SUCCESS, level='info')
      return self.redirect_to('taxi_driver.list')

    self.session.add_flash(messages.TAXI_DRIVER_CREATE_ERROR, level='error')
    return self.redirect_to('taxi_driver.list')

  @role_required(is_admin=True)
  def delete(self, id):
    taxi_driver = TaxiDriver.get_by_id(int(id), parent=self.get_current_account())

    if not taxi_driver:
      self.session.add_flash(messages.TAXI_DRIVER_NOT_FOUND, level='error')
      return self.redirect_to('taxi_driver.list')

    taxi_driver.delete()
    self.session.add_flash(messages.TAXI_DRIVER_DELETE_SUCCESS)

    return self.redirect_to('taxi_driver.list')

  @role_required(is_admin=True)
  def update(self, id):
    taxi_driver = TaxiDriver.get_by_id(int(id), parent=self.get_current_account())

    if not taxi_driver:
      return self.redirect_to('taxi_driver.list', messages.TAXI_DRIVER_NOT_FOUND)

    form = TaxiDriverForm(self.request.POST, obj=taxi_driver)

    if self.request.method == 'POST' and form.validate():
      form.populate_obj(taxi_driver)
      taxi_driver.name = ' '.join((form.data['first_name'],
                                  form.data['last_name']))
      taxi_driver.put()

      self.session.add_flash(messages.TAXI_DRIVER_UPDATE_SUCCESS)
      return self.redirect_to('taxi_driver.list')

    return self.render_to_response('taxi_driver/form.haml', {'form': form})

  def list(self):
    # We pass form so we can generate it with the modal using macros.
    return self.render_to_response('taxi_driver/list.haml', {'form': TaxiDriverForm()})
