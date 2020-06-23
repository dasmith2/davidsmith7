from django.contrib.auth.models import User
from djaveLogin.models import (
    new_login_token, new_sign_up_token, use_token_and_return_user)
from djaveTest.unit_test import TestCase, get_test_user


class LoginTokenTests(TestCase):
  def test_create_and_use_token(self):
    self.assertIsNone(use_token_and_return_user('token_does_not_exist'))

    user = get_test_user()
    token_str = new_login_token(user).token
    self.assertTrue(isinstance(token_str, str))
    self.assertTrue(len(token_str) >= 7)
    self.assertEqual(user, use_token_and_return_user(token_str))
    self.assertIsNone(use_token_and_return_user(token_str))


class SignUpTokenTests(TestCase):
  def test_create_and_use_token(self):
    token_str = new_sign_up_token('test@example.email').token
    self.assertFalse(User.objects.exists())
    user = use_token_and_return_user(token_str)
    self.assertIsNone(use_token_and_return_user(token_str))
    self.assertEqual(1, User.objects.count())
    self.assertEqual('test@example.email', user.email)
    self.assertEqual('test@example.email', user.username)
    self.assertTrue(user.is_active)
