import unittest2

from library import testing
from library import messages
from models.BUS_ROUTE import BUS_ROUTE


class TestBusRouteHandler(testing.TestCase, unittest2.TestCase):

  @testing.login_as(is_manager=True)
  def test_manager_can_create_bus_route(self):
    self.assertLength(0, BUS_ROUTE.all())

    response = self.app.get(self.uri_for('bus_route.list'))
    self.assertOk(response)
    self.assertLength(1, response.pyquery('[data-modal="modal"]'))
    params = {'name': 'Beautiful',
              'description': 'Errr, what you talking about'}
    response = self.app.post(self.uri_for('bus_route.create'), params)
    self.assertRedirects(response, self.uri_for('bus_route.list'))
    self.assertFlashMessage(level='info')

    self.assertLength(1, BUS_ROUTE.all())

  @testing.logged_in
  def test_employee_cannot_create_bus_route(self):
    response = self.app.post(self.uri_for('bus_route.create'))
    self.assertRedirects(response, self.uri_for('home'))

  @testing.login_as(is_editor=True)
  def test_editor_cannot_create_bus_route(self):
    self.assertLength(0, BUS_ROUTE.all())

    response = self.app.post(self.uri_for('bus_route.create'))
    self.assertRedirects(response, self.uri_for('home'))

    self.assertLength(0, BUS_ROUTE.all())

  @testing.login_as(is_manager=True)
  def test_BUS_ROUTE_inputs_have_proper_types(self):
    self.assertLength(0, BUS_ROUTE.all())
    response = self.app.get(self.uri_for('bus_route.list'))

    name_field = response.pyquery('input#name')
    self.assertLength(1, name_field)
    self.assertEqual('text', name_field.attr['type'])
    self.assertEqual('name', name_field.attr['name'])
    #TODO: add check for required field name

    desc_field = response.pyquery('textarea#description')
    self.assertLength(1, desc_field)
    self.assertEqual('description', desc_field.attr['name'])

    self.assertLength(0, BUS_ROUTE.all())

  def test_posting_fails_when_not_logged_in(self):
    self.assertLength(0, BUS_ROUTE.all())
    create_BUS_ROUTE = self.uri_for('bus_route.create')

    response = self.app.post(create_BUS_ROUTE)
    self.assertRedirects(response, self.uri_for('login',
                                                redirect=create_BUS_ROUTE))

    self.assertLength(0, BUS_ROUTE.all())

  @testing.login_as(is_manager=True)
  def test_posting_empty_name_fails(self):
    self.assertLength(0, BUS_ROUTE.all())
    params = {'name': ' ', 'description': 'For testing purposes.'}

    response = self.app.post(self.uri_for('bus_route.create'), params)
    self.assertRedirects(response, self.uri_for('bus_route.list'))
    self.assertLength(0, BUS_ROUTE.all())

  @testing.login_as(is_manager=True)
  def test_duplicate_name_fails(self):
    self.assertLength(0, BUS_ROUTE.all())
    params = {'name': 'Test', 'description': 'For testing purposes.'}

    self.create_BUS_ROUTE(**params)
    self.assertLength(1, BUS_ROUTE.all())

    response = self.app.post(self.uri_for('bus_route.create'), params)
    self.assertOk(response)
    self.assertFlashMessage(messages.BUS_ROUTE_NAME_EXISTS, level='error',
                            response=response)

    self.assertLength(1, BUS_ROUTE.all())

  @testing.login_as(is_manager=True)
  def test_white_space_stripped(self):
    self.assertLength(0, BUS_ROUTE.all())
    params = {'name': 'Test BUS_ROUTE   ',
              'description': 'For testing purposes.   '}
    stripped_name = params['name'].rstrip()
    stripped_description = params['description'].rstrip()

    response = self.app.post(self.uri_for('bus_route.create'), params)
    self.assertRedirects(response, self.uri_for('bus_route.list'))
    self.assertFlashMessage(level='info')

    BUS_ROUTE = self.get_current_account().get_bus_route().filter(
        'name =', stripped_name).get()
    self.assertIsNotNone(BUS_ROUTE)

    self.assertEqual(stripped_name, str(BUS_ROUTE.name))
    self.assertNotEqual(params['name'], str(BUS_ROUTE.name))

    self.assertEqual(stripped_description, str(BUS_ROUTE.description))
    self.assertNotEqual(params['description'], str(BUS_ROUTE.description))

    self.assertLength(1, BUS_ROUTE.all())
