from djavEmail.users_email_config_by_host import users_email_config_by_host
from djaveTest.unit_test import TestCase


class UsersEmailConfigByHostTests(TestCase):
  def test_users_email_config_by_host(self):
    self.assertIsNotNone(users_email_config_by_host('127.0.0.1:8000'))
