from djaveAPI.models.user_api_key import UserAPIKey
from djaveTest import TestCase, get_test_user


class UserAPIKeyTests(TestCase):
  def test_get_user(self):
    user = get_test_user()
    key = UserAPIKey.objects.create_key('The fate of monocultures', user)
    plain_password = key.get_plain_password()
    self.assertEqual(user, UserAPIKey.objects.get_user(
        key.username, plain_password))
