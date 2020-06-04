from djaveAPI.models.user import unique_email_index_exists
from djaveTest.unit_test import TestCase, get_test_user


class TestCreateEmailIndex(TestCase):
  def test_create_email_index(self):
    self.assertFalse(unique_email_index_exists())
    get_test_user()
    self.assertTrue(unique_email_index_exists())
