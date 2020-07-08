from djaveTest.unit_test import TestCase, get_test_user
from djaveStyle.models import get_zoom_override, set_zoom_override


class ZoomPreferenceTests(TestCase):
  def test_get_and_set(self):
    user = get_test_user()
    self.assertIsNone(get_zoom_override(user))
    set_zoom_override(user, 2.2)
    self.assertEqual(2.2, get_zoom_override(user))
