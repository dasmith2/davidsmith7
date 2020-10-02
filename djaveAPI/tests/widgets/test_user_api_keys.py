from djaveTest.unit_test import TestCase
from djaveAPI.widgets.user_api_keys import UserAPIKeys


class UserApiKeysTests(TestCase):
  def test_display(self):
    UserAPIKeys('/whatever').as_html()
