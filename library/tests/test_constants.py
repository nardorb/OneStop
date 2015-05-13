import unittest2

from library import constants
from library import testing


class TestLibraryConstants(testing.TestCase, unittest2.TestCase):

  def test_public_domain(self):
    self.assertEqual('transapptool.appspot.com', constants.PUBLIC_DOMAIN)

  def test_public_host(self):
    self.assertEqual('http://www.transapptool.appspot.com', constants.PUBLIC_HOST)

  def test_support_email(self):
    self.assertEqual('support@transapptool.appspot.com', constants.SUPPORT_EMAIL)

  def test_contact_email(self):
    self.assertEqual('contact@transapptool.appspot.com', constants.CONTACT_EMAIL)

