from webapp2_extras import auth

from forms.order import OrderForm
from forms.assign_driver import AssignDriverForm
from handlers import base
from library import messages
from library.auth import login_required
from library.auth import role_required
from models.order import Order
from models.taxi_driver import TaxiDriver


class OrderHandler(base.BaseHandler):

  @login_required
  def create(self):
    form = OrderForm(self.request.POST)

    if self.request.method == 'POST' and form.validate():

      order = Order(origin=form.data['origin'],
                destination=form.data['destination'],
                passengers=form.data['passengers'],
                comments=form.data['comments'],
                vehicle_type=form.data['vehicle_type'],
                cost=form.data['cost'],
                profile=self.get_current_profile(),
                parent=self.get_current_account())
      order.put()

      self.session.add_flash(messages.ORDER_CREATE_SUCCESS, level='info')
      return self.redirect_to('home')

    self.session.add_flash(messages.ORDER_CREATE_ERROR, level='error')
    return self.redirect_to('contact')

  @role_required(is_admin=True)
  def delete(self, id):
    order = Order.get_by_id(int(id), parent=self.get_current_account())

    if not order:
      self.session.add_flash(messages.ORDER_NOT_FOUND, level='error')
      return self.redirect_to('order.list')

    order.delete()
    self.session.add_flash(messages.ORDER_DELETE_SUCCESS)

    return self.redirect_to('order.list')


  @role_required(is_admin=True)
  def list(self):
    # We pass form so we can generate it with the modal using macros.
    return self.render_to_response('order/list.haml', {'form': OrderForm()})


  @role_required(is_admin=True)
  def assign_driver(self, id):
    order = Order.get_by_id(int(id), parent=self.get_current_account())

    if not order:
      return self.redirect_to('order.list', messages.ORDER_NOT_FOUND)

    form = AssignDriverForm(self.request.POST, obj=order)

    if self.request.method == 'POST' and form.validate():
      taxiDriver = TaxiDriver.get_by_driver_id(form.data['driver_id'])
      order.driver = taxiDriver.key()
      order.put()

      self.session.add_flash(messages.TAXI_DRIVER_ASSIGN_SUCCESS)
      return self.redirect_to('order.list')
    # Unable to flash ASS_DRIVER_ERROR because request returns 302.
    # Form may not be validating correctly in the above, hence the
    # the form call below is the one that actually renders the
    # correct form.
    return self.render_to_response('order/form.haml', {'form': form})

  # @login_required
  # def update(self, id):
  #   order = Order.get_by_id(int(id), parent=self.get_current_account())

  #   if not order:
  #     return self.redirect_to('order.list', messages.ORDER_NOT_FOUND)

  #   form = OrderForm(self.request.POST, obj=order)

  #   if self.request.method == 'POST' and form.validate():
  #     form.populate_obj(order)
  #     order.put()

  #     self.session.add_flash(messages.ORDER_UPDATE_SUCCESS)
  #     return self.redirect_to('order.list')

  #   return self.render_to_response('order/form.haml', {'form': form})