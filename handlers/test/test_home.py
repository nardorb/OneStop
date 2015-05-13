from google.appengine.api import memcache

import unittest2

from library import testing


class TestHomeHandler(testing.TestCase, unittest2.TestCase):
  def test_home_page_uses_home_template(self):
    response = self.app.get(self.uri_for('home'))
    self.assertOk(response)
    self.assertTemplateUsed('corporate/home.haml')

  def test_home_page_uses_cache(self):
    # Cache should start empty.
    self.assertEqual(0, memcache.get_stats()['items'])

    # After we retrieve the homepage, the cache should be primed
    response = self.app.get(self.uri_for('home'))
    self.assertEqual(1, memcache.get_stats()['items'])

    # If we get the home page again, we should have a single hit
    response = self.app.get(self.uri_for('home'))
    self.assertOk(response)
    self.assertEqual(1, memcache.get_stats()['hits'])
