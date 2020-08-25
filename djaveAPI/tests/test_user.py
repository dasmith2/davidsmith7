from djaveAPI.models.user import unique_email_index_exists
try:
  from djaveRelease.signals import post_release
except ModuleNotFoundError:
  post_release = None
from djaveTest.unit_test import TestCase


class TestCreateEmailIndex(TestCase):
  def test_create_email_index(self):
    if post_release:
      self.assertFalse(unique_email_index_exists())
      post_release.send(sender=None)
      self.assertTrue(unique_email_index_exists())
