import unittest2

from library import testing


class TestLoginHandler(testing.TestCase, unittest2.TestCase):

  def test_get_login_page(self):
    response = self.app.get(self.uri_for('login'))
    self.assertEqual(200, response.status_int)
    self.assertIn('Login', response.body)

  def test_get_login_page_with_redirect(self):
    email, password = 'test@example.org', 'mypass'
    self.create_profile(email, password)

    original_page = self.uri_for('profile.view')
    login_redirect = self.uri_for('login', redirect=original_page)

    # Try to go to a protected page.
    response = self.app.get(original_page)
    self.assertRedirects(response, login_redirect)

    # Load up the page that it redirected us to.
    response = self.app.post(response.location, {'email': email,
                                                 'password': password})
    self.assertRedirects(response, original_page)

  def test_login(self):
    email, password = 'test@example.org', 'pass'
    self.create_profile(email, password)

    # First test that we're not logged in:
    response = self.app.get(self.uri_for('profile.view'))
    self.assertRedirects(response)

    # Log us in.
    response = self.app.post(self.uri_for('login'), {'email': email,
                                                     'password': password})
    self.assertRedirects(response, self.uri_for('home'))

    # Test that we can now view that page.
    response = self.app.get(self.uri_for('profile.view'))
    self.assertOk(response)

  @testing.logged_in
  def test_login_already_logged_in(self):
    response = self.app.get(self.uri_for('login'))
    self.assertRedirects(response, self.uri_for('home'))

  def test_not_beta_tester(self):
    email, password = 'test@example.org', 'pass',
    self.create_profile(email, password, beta_tester=False)

    # First test that we're not logged in:
    self.assertNotLoggedIn()

    # Log us in, and fail.
    login_data = {'email': email, 'password': password}
    response = self.app.post(self.uri_for('login'), login_data)

    # Redirects back to the login page with error.
    self.assertRedirects(response, self.uri_for('login'))
