from djaveLogin.models import new_token, use_token_and_return_user
from djaveTest import TestCase, get_test_user


class LoginTokenTests(TestCase):
  def test_create_and_use_token(self):
    self.assertIsNone(use_token_and_return_user('token_does_not_exist'))

    user = get_test_user()
    token = new_token(user)
    self.assertTrue(isinstance(token, str))
    self.assertTrue(len(token) > 16)
    self.assertEqual(user, use_token_and_return_user(token))
    self.assertIsNone(use_token_and_return_user(token))
