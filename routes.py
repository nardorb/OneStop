from webapp2_extras.routes import RedirectRoute

from handlers.home import HomeHandler
from handlers.login import LoginHandler
from handlers.profile import ProfileHandler
from handlers.signup import SignupHandler
from handlers.driver_signup import DriverSignupHandler
from handlers.static import PublicStaticHandler
from handlers.contact import ContactHandler
from handlers.taxi import TaxiHandler
from handlers.taxi_driver import TaxiDriverHandler
from handlers.order import OrderHandler


__all__ = ['application_routes']

application_routes = []

_route_info = [
    # Public (static) handlers.
    ('driver_signup', 'GET', '/driver_signup/',
        PublicStaticHandler('driver-signup.html'), 'get'),
    ('about', 'GET', '/about/',
        PublicStaticHandler('about.html'), 'get'),
    ('copyright', 'GET', '/copyright/',
        PublicStaticHandler('coming_soon.haml'), 'get'),
    ('faq', 'GET', '/faq/',
        PublicStaticHandler('coming_soon.haml'), 'get'),
    ('features', 'GET', '/features/',
        PublicStaticHandler('coming_soon.haml'), 'get'),
    ('privacy', 'GET', '/privacy/',
        PublicStaticHandler('coming_soon.haml'), 'get'),
    ('terms', 'GET', '/terms/',
        PublicStaticHandler('coming_soon.haml'), 'get'),

    # Public handlers.
    ('contact', None, '/contact/', ContactHandler, 'contact'),
    ('home', 'GET', '/', HomeHandler, 'home'),
    ('signup', None, '/signup/', SignupHandler, 'signup'),
    ('driver_signup', None, '/driver_signup/', DriverSignupHandler, 'driver_signup'),

    # Authentication-related handlers.
    ('login', None, '/login/', LoginHandler, 'login'),
    ('logout', 'GET', '/logout/', LoginHandler, 'logout'),
    ('forgot-password', None, '/forgot-password/',
        LoginHandler, 'forgot_password'),

    ('order.create', None, '/order/create/', OrderHandler, 'create'),
    ('order.list', None, '/order/', OrderHandler, 'list'),
    ('order.assign_driver', None, '/order/<id:\d+>/assign_driver/',
        OrderHandler, 'assign_driver'),
    ('order.delete', None, '/order/<id:\d+>/delete/',
        OrderHandler, 'delete'),

    ('profile.activate', None, '/profile/activate/',
        ProfileHandler, 'activate'),
    ('profile.view', None, '/profile/', ProfileHandler, 'view'),

    ('taxi.create', None, '/taxi/create/', TaxiHandler, 'create'),
    ('taxi.delete', None, '/taxi/<id:\d+>/delete/',
        TaxiHandler, 'delete'),
    ('taxi.set_driver', None, '/taxi/<id:\d+>/set_driver/',
        TaxiHandler, 'set_driver'),
    ('taxi.list', None, '/taxi/', TaxiHandler, 'list'),
    ('taxi.update', None, '/taxi/<id:\d+>/update/',
        TaxiHandler, 'update'),

    ('taxi_driver.create', None, '/taxi_driver/create/', TaxiDriverHandler, 'create'),
    ('taxi_driver.delete', None, '/taxi_driver/<id:\d+>/delete/',
        TaxiDriverHandler, 'delete'),
    ('taxi_driver.list', None, '/taxi_driver/', TaxiDriverHandler, 'list'),
    ('taxi_driver.update', None, '/taxi_driver/<id:\d+>/update/',
        TaxiDriverHandler, 'update'),
]

for name, methods, pattern, handler_cls, handler_method in _route_info:
  # Allow a single string, but this has to be changed to a list.
  if isinstance(methods, basestring):
    methods = [methods]

  # Create the route.
  route = RedirectRoute(name=name, template=pattern, methods=methods,
                        handler=handler_cls, handler_method=handler_method)

  # Add the route to the proper public list.
  application_routes.append(route)
