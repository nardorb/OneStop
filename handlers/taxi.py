from forms.taxi import TaxiForm
# from forms.bus_time import BusTimeForm
from forms.assign_driver import AssignDriverForm
from handlers import base
from library import messages
from library.auth import role_required
from models.taxi import Taxi
from models.taxi_driver import TaxiDriver


class TaxiHandler(base.BaseHandler):

  @role_required(is_admin=True)
  def create(self):
    form = TaxiForm(self.request.POST)

    if self.request.method == 'POST' and form.validate():

      if Taxi.get_by_license_plate(form.data['license_plate']):
        self.session.add_flash(messages.TAXI_EXISTS,
                               level='error')
        return self.render_to_response('taxi/form.haml', {'form': form})


      taxi = Taxi(license_plate=form.data['license_plate'],
                is_operational=form.data['is_operational'],
                make=form.data['make'],
                model=form.data['model'],
                vehicle_type=form.data['vehicle_type'],
                color=form.data['color'],

                # taxi_driver=form.data['driver_id'],
                parent=self.get_current_account())
      taxi.put()

      self.session.add_flash(messages.TAXI_CREATE_SUCCESS, level='info')
      return self.redirect_to('taxi.list')

    self.session.add_flash(messages.TAXI_CREATE_ERROR, level='error')
    return self.redirect_to('taxi.list')

  @role_required(is_admin=True)
  def delete(self, id):
    taxi = Taxi.get_by_id(int(id), parent=self.get_current_account())

    if not bus:
      self.session.add_flash(messages.TAXI_NOT_FOUND, level='error')
      return self.redirect_to('taxi.list')

    taxi.delete()
    self.session.add_flash(messages.TAXI_DELETE_SUCCESS)

    return self.redirect_to('taxi.list')

  def list(self):
    # We pass form so we can generate it with the modal using macros.
    return self.render_to_response('taxi/list.haml', {'form': TaxiForm()})

  # May be depreciated
  # check before release
  @role_required(is_admin=True)
  def assign_driver(self, id):
    taxi = Taxi.get_by_id(int(id), parent=self.get_current_account())

    if not taxi:
      return self.redirect_to('taxi.list', messages.TAXI_NOT_FOUND)

    form = AssignDriverForm(self.request.POST, obj=taxi)

    if self.request.method == 'POST' and form.validate():
      taxiDriver = TaxiDriver.get_by_driver_id(form.data['driver_id'])
      taxi.taxi_driver = taxiDriver.key()
      taxi.put()

      self.session.add_flash(messages.TAXI_DRIVER_ASSIGN_SUCCESS)
      return self.redirect_to('taxi.list')
    # Unable to flash ASS_DRIVER_ERROR because request returns 302.
    # Form may not be validating correctly in the above, hence the
    # the form call below is the one that actually renders the
    # correct form.
    return self.render_to_response('taxi/form.haml', {'form': form})


  @role_required(is_admin=True)
  def update(self, id):
    taxi = Taxi.get_by_id(int(id), parent=self.get_current_account())

    if not taxi:
      return self.redirect_to('taxi.list', messages.TAXI_NOT_FOUND)

    form = TaxiForm(self.request.POST, obj=taxi)

    if self.request.method == 'POST' and form.validate():
      form.populate_obj(taxi)
      taxi.put()

      self.session.add_flash(messages.TAXI_UPDATE_SUCCESS)
      return self.redirect_to('taxi.list')

    return self.render_to_response('taxi/form.haml', {'form': form})