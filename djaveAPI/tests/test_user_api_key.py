from djaveAPI.models.user_api_key import UserAPIKey
from djaveAPI.tests.test_api_key import set_api_key_stuff
from djaveTest import TestCase, get_test_user


def get_test_user_api_key(**kwargs):
  user = kwargs.get('user', None)
  if not user:
    user = get_test_user()
  return set_api_key_stuff(UserAPIKey(user=user), **kwargs)


class UserAPIKeyTests(TestCase):
  def test_get_user(self):
    user = get_test_user()
    key = UserAPIKey.objects.create_key('The_fate_of_monocultures', user=user)
    plain_password = key.get_plain_password()
    self.assertEqual(user, UserAPIKey.objects.get_user(
        key.username, plain_password))
