import unittest2

from library import testing


class TestNavbar(testing.TestCase, unittest2.TestCase):

  @testing.logged_in
  def test_navbar_rendered_on_dashboard(self):
    response = self.app.get(self.uri_for('home'))
    self.assertTemplateUsed('corporate/private_base.haml',
                            'components/corporate/navbar_private.haml')
    self.assertLength(1, response.pyquery('div.navbar'))

  @testing.logged_in
  def test_private_navbar_always_rendered_when_logged_in(self):
    response = self.app.get(self.uri_for('contact'))
    self.assertTemplateUsed('public_base.haml',
                            'components/navbar_private.haml')
    self.assertLength(1, response.pyquery('div.navbar'))

  def test_public_navbar_rendered_when_not_logged_in(self):
    response = self.app.get(self.uri_for('home'))
    self.assertTemplateUsed('corporate/public_base.haml',
                            'components/corporate/navbar_public.haml')
    self.assertLength(1, response.pyquery('div.navbar'))
