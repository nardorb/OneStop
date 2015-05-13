import base64
from itertools import chain, combinations

from google.appengine.ext import deferred
import unittest2

from library import testing
from models.profile import Profile


@unittest2.skip
class TestSignupHandler(testing.TestCase, unittest2.TestCase):
  SIGNUP_DATA = {'name': 'Test Name', 'email': 'test@example.org',
                 'password': 'pass', 'company_name': 'Test Company'}

  def test_signup(self):
    response = self.app.get(self.uri_for('signup'))
    self.assertOk(response)
    self.assertTemplateUsed('signup.html')

  def test_signup_inputs_have_proper_types(self):
    # We rely on some client-side browser-built-in validation with fields,
    # so we should check that we don't accidentally change an email field
    # to a text field.
    response = self.app.get(self.uri_for('signup'))

    email_field = response.pyquery('input#email')
    self.assertLength(1, email_field)
    self.assertEqual('email', email_field.attr['type'])
    self.assertEqual('email', email_field.attr['name'])
    self.assertIsNotNone(email_field.attr['required'])

    name_field = response.pyquery('input#name')
    self.assertLength(1, name_field)
    self.assertEqual('text', name_field.attr['type'])
    self.assertEqual('name', name_field.attr['name'])
    self.assertIsNotNone(name_field.attr['required'])

    company_name_field = response.pyquery('input#company_name')
    self.assertLength(1, company_name_field)
    self.assertEqual('text', company_name_field.attr['type'])
    self.assertEqual('company_name', company_name_field.attr['name'])
    self.assertIsNotNone(company_name_field.attr['required'])

    password_field = response.pyquery('input#password')
    self.assertLength(1, password_field)
    self.assertEqual('password', password_field.attr['type'])
    self.assertEqual('password', password_field.attr['name'])
    self.assertIsNotNone(password_field.attr['required'])

  def test_post_signup_missing_data(self):
    # Required fields are: name, email, password, company_name
    # If any of these are missing, an error should happen:

    # This isn't the entire powerset. The entire set is ignored (since that
    # would be valid).
    powerset = chain.from_iterable(combinations(self.SIGNUP_DATA.keys(), size)
                                   for size in range(len(self.SIGNUP_DATA)))
    for field_list in powerset:
      data = dict((k, self.SIGNUP_DATA[k]) for k in field_list)
      response = self.app.post(self.uri_for('signup'), data)
      self.assertOk(response)
      self.assertTemplateUsed('signup.html')

      for field_name in self.SIGNUP_DATA:
        field = response.pyquery('input#%s' % field_name)
        self.assertLength(1, field)

        if field_name in data:
          # We provided this field so it should be fine
          self.assertEqual('', field.attr['data-error'],
                           field_name + ' should not have errors.')
        else:
          # This field was missing, so we should have an error
          self.assertNotEqual('', field.attr['data-error'],
                              field_name + ' should have an error.')

  def test_signup_page_flow(self):
    # Check that things are empty
    self.assertLength(0, Profile.all())

    # Sign up with the form
    response = self.app.post(self.uri_for('signup'), self.SIGNUP_DATA)
    self.assertRedirects(response, self.uri_for('dashboard', tour=''))

    # Check that we are actually logged in
    response = self.app.get(response.location)
    self.assertLoggedIn()

    # Check that one of everything was created
    self.assertLength(1, Profile.all())

    profile = Profile.all().get()

    # Check the basic data
    self.assertEqual(self.SIGNUP_DATA['email'], profile.email)
    self.assertEqual(self.SIGNUP_DATA['name'], profile.name)

    # Logout and log back in to test that the password works
    self.logout()
    response = self.login(self.SIGNUP_DATA['email'],
                          self.SIGNUP_DATA['password'])
    self.assertRedirects(response, self.uri_for('dashboard'))

  def test_signup_sends_welcome_email(self):
    # Sign up successfully
    response = self.app.post(self.uri_for('signup'), self.SIGNUP_DATA)
    self.assertRedirects(response, self.uri_for('dashboard', tour=''))

    # Check that a profile was created
    profile = Profile.get_by_email(self.SIGNUP_DATA['email'])
    self.assertIsNotNone(profile)

    # Check that a mail-sending task is in the queue
    tasks = self.taskqueue_stub.GetTasks('mail')
    self.assertLength(1, tasks)

    # Run the task (it should be a deferred call) and check that an e-mail
    # is sent
    task, = tasks
    deferred.run(base64.b64decode(task['body']))
    messages = self.mail_stub.get_sent_messages()
    self.assertLength(1, messages)

    message, = messages
    self.assertEqual('"%s" <%s>' % (profile.name, profile.email), message.to)
    self.assertEqual('Welcome to Daily Meeting!', message.subject)
    self.assertEqual('"Daily Meeting" <noreply@dailymeetingapp.com>',
                     message.sender)
    self.assertEqual('"Daily Meeting Support" <support@dailymeetingapp.com>',
                     message.reply_to)
    activation_key = Profile.all().get().activation_key
    activation_url = self.uri_for('profile.activate', k=activation_key)
    self.assertIn(activation_url, message.body.decode())
    self.assertIn(activation_url, message.html.decode())

  def test_signup_welcome_email_has_proper_public_host(self):
    response = self.app.post(self.uri_for('signup'), self.SIGNUP_DATA)
    self.assertRedirects(response, self.uri_for('dashboard', tour=''))

    # Check that a mail-sending task is in the queue.
    tasks = self.taskqueue_stub.GetTasks('mail')
    self.assertLength(1, tasks)
    task, = tasks
    deferred.run(base64.b64decode(task['body']))
    messages = self.mail_stub.get_sent_messages()
    self.assertLength(1, messages)
    message, = messages
    self.assertNotIn('http://localhost', message.body.decode())
    self.assertNotIn('http://localhost', message.html.decode())
    self.assertIn('http://www.dailymeetingapp.com', message.body.decode())
    self.assertIn('http://www.dailymeetingapp.com', message.html.decode())

  def test_signup_with_existing_email(self):
    response = self.app.post(self.uri_for('signup'), self.SIGNUP_DATA)
    self.assertRedirects(response)
    self.assertLength(1, Profile.all())

    response = self.app.post(self.uri_for('signup'), self.SIGNUP_DATA)
    self.assertOk(response)
    self.assertLength(1, Profile.all())

    email_field = response.pyquery('input#email')
    self.assertLength(1, email_field)
    self.assertNotEqual('', email_field.attr['data-error'])

  def test_signup_schedules_emails(self):
    # Sign up successfully.
    response = self.app.post(self.uri_for('signup'), self.SIGNUP_DATA)
    self.assertRedirects(response, self.uri_for('dashboard', tour=''))

    # Check that a profile was created.
    profile = Profile.get_by_email(self.SIGNUP_DATA['email'])
    self.assertIsNotNone(profile)

    # There should be one task in the scheduler queue.
    tasks = self.taskqueue_stub.get_filtered_tasks(queue_names=['scheduler'])
    self.assertLength(1, tasks)

    # Verify the details about the task are correct.
    task, = tasks
    self.assertEqual(self.uri_for('mail.schedule'), task.url)
    self.assertEqual(str(profile.get_account().key()),
                     task.extract_params()['account_key'])

  def test_signup_schedules_payment_create_call(self):
    # Sign up successfully.
    response = self.app.post(self.uri_for('signup'), self.SIGNUP_DATA)
    self.assertRedirects(response, self.uri_for('dashboard', tour=''))

    # Check that a profile was created.
    profile = Profile.get_by_email(self.SIGNUP_DATA['email'])
    self.assertIsNotNone(profile)

    # There should be one task in the scheduler queue.
    tasks = self.taskqueue_stub.get_filtered_tasks(queue_names=['payment'])
    self.assertLength(1, tasks)

    # Verify the details about the task are correct.
    task, = tasks
    self.assertEqual(self.uri_for('payment.create'), task.url)
    self.assertEqual(str(profile.key()), task.extract_params()['profile_key'])

  def test_signup_page_has_link_to_terms(self):
    response = self.app.get(self.uri_for('signup'))
    self.assertLength(1, response.pyquery('.signup a[href="%s"]' % (
                                          self.uri_for('terms'))))

  def test_signup_page_has_link_to_privacy_policy(self):
    response = self.app.get(self.uri_for('signup'))
    self.assertLength(1, response.pyquery('.signup a[href="%s"]' % (
                                          self.uri_for('privacy'))))

  def test_signup_next_page_has_conversion_pixel(self):
    response = self.app.post(self.uri_for('signup'), self.SIGNUP_DATA)
    self.assertRedirects(response)

    # Load the dashboard page and check that the conversion tracker was used.
    response = self.app.get(self.uri_for('dashboard'))
    self.assertOk(response)
    self.assertTemplateUsed('components/conversion_tracker.html')

    # Load it a second time and make sure it's *not* used.
    response = self.app.get(self.uri_for('dashboard'))
    self.assertOk(response)
    self.assertTemplateNotUsed('components/conversion_tracker.html')
