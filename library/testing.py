from contextlib import contextmanager
from functools import wraps
import logging
import os

from google.appengine.datastore import datastore_stub_util
from google.appengine.ext import testbed
import mock
import webapp2
import webapp2_extras
import webtest

from library import csrf
import main
from main import app
from models.account import Account
from models.busroute import BusRoute
from models.profile import Profile
from models.receipt import Receipt

__all__ = ['logged_in', 'login_as', 'TestCase']


ROOT_PATH = os.path.dirname(main.__file__)
HR_LOW_CONSISTENCY_POLICY = (datastore_stub_util
                             .PseudoRandomHRConsistencyPolicy(probability=0))
HR_HIGH_CONSISTENCY_POLICY = (datastore_stub_util
                              .PseudoRandomHRConsistencyPolicy(probability=1))


class TestCase(object):
  # Default values
  # ==============
  DEFAULT_EMAIL = 'test@example.org'
  DEFAULT_PASSWORD = 'passwr0d'
  DEFAULT_COMPANY_NAME = 'Test Company'
  DEFAULT_ROUTE_NUMBER = '44'
  DEFAULT_BUS_STOPS = '6'
  DEFAULT_TEAM_NAME = 'My Team'
  DEFAULT_PROFILE_NAME = 'Test Profile'

  # Custom headers for requests
  # ===========================
  CRON_HEADERS = {'X-Appengine-Cron': 'true'}
  TASKQUEUE_HEADERS = {'X-AppEngine-QueueName': 'default'}

  # Standard TestCase setUp and tearDown
  # ====================================

  def setUp(self):
    if hasattr(super(TestCase, self), 'setUp'):
      super(TestCase, self).setUp()
    self.configure_appengine()
    self.configure_app()
    self.configure_csrf()
    self.configure_jinja2()
    self.configure_timezone()

    # HTTP_HOST is required for any handlers that hit the task queue
    if 'HTTP_HOST' not in os.environ:
      os.environ['HTTP_HOST'] = 'localhost:80'

  def tearDown(self):
    self.testbed.deactivate()

  # Configuration helpers
  # =====================

  def configure_appengine(self):
    self.testbed = testbed.Testbed()
    self.testbed.activate()
    self.testbed.init_datastore_v3_stub()
    self.testbed.init_mail_stub()
    self.testbed.init_memcache_stub()
    self.testbed.init_taskqueue_stub(root_path=ROOT_PATH)

    self.mail_stub = self.testbed.get_stub(testbed.MAIL_SERVICE_NAME)
    self.taskqueue_stub = self.testbed.get_stub(testbed.TASKQUEUE_SERVICE_NAME)
    self.datastore_stub = self.testbed.get_stub(testbed.DATASTORE_SERVICE_NAME)
    self.datastore_stub._consistency_policy = HR_HIGH_CONSISTENCY_POLICY

  @contextmanager
  def datastore_consistency_policy(self, policy):
    """A context manager that allows us to modify the consistency policy for
    certain tests, so we can simulate the behaviour of the High Replication
    Datastore.

    Example:

      with self.datastore_consistency_policy(POLICY):
        do_something_that_uses_transactions()

    """
    prev_policy = self.datastore_stub._consistency_policy
    self.datastore_stub._consistency_policy = policy
    yield
    self.datastore_stub._consistency_policy = prev_policy

  def configure_app(self):
    app.set_globals(app=app, request=self.get_request())

    if not hasattr(self, 'app'):
      self.app = webtest.TestApp(app)

  def configure_csrf(self, enabled=False):
    if not hasattr(csrf.CSRF, '_original_token_required'):
      csrf.CSRF._original_token_required = csrf.CSRF.token_required

    if enabled:
      token_required = csrf.CSRF._original_token_required
    else:
      token_required = mock.Mock(return_value=False)

    csrf.CSRF.token_required = token_required

  def configure_jinja2(self):
    """Hook into Jinja2's template loader to track which templates are used."""
    # Make sure the app is configured:
    self.configure_app()

    # Keep track of a few things (this test case, the template loader, the
    # original get_source method)
    test_case = self
    environment = self.get_jinja2().environment
    original_get_source = environment.loader.get_source
    original_do_request = self.app.do_request

    # These *could* be defined elsewhere, but we don't want them if we don't
    # call configure_jinja2, so we assign these instance methods and vars here
    test_case._templates_used = []

    def get_templates_used():
      return test_case._templates_used

    def assertTemplateUsed(*templates):
      for template in templates:
        test_case.assertIn(template, test_case.get_templates_used())

    def assertTemplateNotUsed(*templates):
      for template in templates:
        test_case.assertNotIn(template, test_case.get_templates_used())

    test_case.get_templates_used = get_templates_used
    test_case.assertTemplateUsed = assertTemplateUsed
    test_case.assertTemplateNotUsed = assertTemplateNotUsed

    # Ensure that we are never pulling from the cache (otherwise, get_source
    # will never get called).
    environment.cache = None

    # Inject our own version of get_source (rather than an entire Loader)
    def get_source(environment, template):
      test_case._templates_used.append(template)
      return original_get_source(environment, template)

    environment.loader.get_source = get_source

    # Inject into WebTest's do_request method so that we clear the templates
    # on each request
    def do_request(*args, **kwargs):
      test_case._templates_used = []
      return original_do_request(*args, **kwargs)

    self.app.do_request = do_request

  def configure_timezone(self):
    os.environ['TZ'] = 'UTC'

  # Special getters
  # ===============

  @classmethod
  def get_request(cls):
    request = webapp2.Request.blank('/')
    request.app = app
    return request

  @classmethod
  def get_auth(cls):
    return webapp2_extras.auth.get_auth(request=cls.get_request())

  @classmethod
  def get_jinja2(cls):
    return webapp2_extras.jinja2.get_jinja2(app=app)

  @classmethod
  def uri_for(cls, name, *args, **kwargs):
    return webapp2.uri_for(name, cls.get_request(), *args, **kwargs)

  @classmethod
  def create_account(cls, name=None):
    if not name:
      name = cls.DEFAULT_COMPANY_NAME

    account = Account(name=name)
    account.put()
    return account

  @classmethod
  def create_bus_route(cls, route_number=None, stops=None, account=None):
    if not route_number:
      route_number = cls.DEFAULT_ROUTE_NUMBER

    if not stops:
      stops = cls.DEFAULT_BUS_STOPS

    if not account:
      account = cls.create_account()

    busroute = BusRoute(route_number=name, stops=stops, parent=account)
    busroute.put()
    return busroute

  @classmethod
  def create_receipt(cls, currency=None, amount=None, access_code=None,
                     profile=None):

    if not currency:
      currency = Receipt.Currency.Default

    if not profile:
      profile = cls.create_profile()

    receipt = Receipt(amount=amount, access_code=access_code,
                      currency=currency, profile=profile)
    receipt.put()
    return receipt

  @classmethod
  def create_profile(cls, email=None, password=None, beta_tester=True,
                     is_admin=False, is_manager=False, is_editor=False,
                     activated=True, account=None):
    # TODO: Move this into a top level function (testing.create_profile)
    # Use defaults if anything here is missing.
    UserModel = cls.get_auth().store.user_model

    if not email:
      # Generate an e-mail that should be unique...
      email = '%s-%s' % (UserModel.query().count(), cls.DEFAULT_EMAIL)
    password = password or cls.DEFAULT_PASSWORD

    # Create the auth.user_model.
    ok, user = UserModel.create_user(email, password_raw=password)

    if not ok:
      raise Exception('Error creating auth.User: %s' % email)

    if not account:
      account = cls.create_account()

    # Create the profile.
    profile = Profile(name=cls.DEFAULT_PROFILE_NAME, is_admin=is_admin,
                      is_manager=is_manager, is_editor=is_editor,
                      email=email, beta_tester=beta_tester,
                      activated=activated, auth_user_id=user.key.id(),
                      timezone='UTC', parent=account)
    profile.put()

    # Return the profile (we can get everything else with that)
    return profile

  # Authentication-related methods
  # ==============================
  def login(self, email=None, password=None):
    login_data = {'email': email or self.DEFAULT_EMAIL,
                  'password': password or self.DEFAULT_PASSWORD}
    return self.app.post(self.uri_for('login'), login_data)

  def logout(self):
    return self.app.get(self.uri_for('logout'))

  # Custom assert methods
  # =====================
  def assertRaisesWithMessage(self, msg, func, *args, **kwargs):
    try:
      func(*args, **kwargs)
      self.assertFail()
    except Exception as inst:
      self.assertEqual(inst.message, msg)

  def assertOk(self, response, message=None):
    self.assertEqual(200, response.status_int, message)

  def assertRedirects(self, response, uri=None):
    self.assertTrue(str(response.status_int).startswith('30'),
                    'Expected 30X, got %s' % response.status_int)
    if not uri:
      self.assertTrue(response.location)
    else:
      if not uri.startswith('http'):
        uri = 'http://localhost' + uri

      self.assertEqual(uri, response.location)

  def assertNotFound(self, response):
    self.assertEqual(404, response.status_int)

  def assertLoggedIn(self):
    response = self.app.get(self.uri_for('login'))
    self.assertRedirects(response)

  def assertNotLoggedIn(self):
    response = self.app.get(self.uri_for('login'))
    self.assertOk(response)

  def assertLength(self, expected_length, collection):
    try:
      actual_length = collection.count()
    except:
      actual_length = len(collection)

    self.assertEqual(expected_length, actual_length)

  def assertFlashMessage(self, message=None, level=None, response=None):
    response = response or self.app.get(self.uri_for('home'))
    self.assertOk(response)
    self.assertLength(1, response.pyquery('#notification-bar'))

    if message:
      self.assertEqual(
          message, response.pyquery('#notification-bar .alert div').text())

    if level:
      self.assertTrue(response.pyquery('#notification-bar .alert').hasClass(
                      'alert-%s' % level))


class login_as(object):
  def __init__(self, email=None, password=None,
               is_admin=False, is_manager=False, is_editor=False):
    self.email = email or TestCase.DEFAULT_EMAIL
    self.password = password or TestCase.DEFAULT_PASSWORD
    self.is_admin = is_admin or False
    self.is_manager = is_manager or False
    self.is_editor = is_editor or False

  def __call__(self, test):
    @wraps(test)
    def wrapped_test(test_case, *args, **kwargs):
      profile = test_case.create_profile(email=self.email,
                                         password=self.password,
                                         is_admin=self.is_admin,
                                         is_manager=self.is_manager,
                                         is_editor=self.is_editor)
      test_case.login(self.email, self.password)
      test_case.current_profile = profile
      test_case.get_current_account = lambda: profile.get_account()
      test_case.get_current_profile = lambda: profile
      return test(test_case, *args, **kwargs)
    return wrapped_test


logged_in = login_as()


@contextmanager
def silence_logging():
  """A context manager that allows us to silence logging.

  Example:

    with silence_logging():
      call_method_that_logs_something()

  """
  log = logging.getLogger()
  log.setLevel(99)
  yield
  log.setLevel(30)
