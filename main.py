import webapp2

from config import webapp2_config
from routes import application_routes


app = webapp2.WSGIApplication(routes=application_routes, config=webapp2_config)
