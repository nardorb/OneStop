import unittest2

from library import constants
from library import testing


class TestFooter(testing.TestCase, unittest2.TestCase):

  def test_footer_has_proper_links(self):
    response = self.app.get(self.uri_for('home'))
    self.assertOk(response)
    footer = response.pyquery('footer')
    self.assertLength(1, footer)

    self.assertEqual(constants.PUBLIC_BLOG,
                     footer.find('#social-blog').attr('href'))

    self.assertEqual(constants.PUBLIC_BLOG + '/feed/',
                     footer.find('#social-rss').attr('href'))

    self.assertEqual(constants.PUBLIC_FACEBOOK,
                     footer.find('#social-facebook').attr('href'))

    self.assertEqual(constants.PUBLIC_TWITTER,
                     footer.find('#social-twitter').attr('href'))
