from djaveTest.unit_test import TestCase, get_test_user
from djaveStyle.models import get_zoom_override
from djaveStyle.widgets.zoom_preference import ZoomPreference


class ZoomPreferenceTests(TestCase):
  def test_set(self):
    user = get_test_user()
    request = None

    # Bump it up
    request_POST = {
        'hiddenautomaticzoom': '2.0',
        'zoomin': 'yep'}
    ZoomPreference(request, request_POST, user)
    self.assertEqual(2.1, get_zoom_override(user))

    # Bump it back down
    request_POST = {
        'hiddenautomaticzoom': '1000.0',
        'zoomout': 'yep'}
    ZoomPreference(request, request_POST, user)
    self.assertEqual(2.0, get_zoom_override(user))

    # Clear it out
    request_POST = {
        'hiddenautomaticzoom': '1000.0',
        'automatic': 'yep'}
    ZoomPreference(request, request_POST, user)
    self.assertIsNone(get_zoom_override(user))
