from django.contrib.auth.models import User
from djaveClassMagic.signals import do_destroy_user

from tracktime.tests.test_case_with_data import TestCaseWithData


class DestroyUserTests(TestCaseWithData):
  def test_destroy(self):
    self.setup_everything()
    do_destroy_user(self.user)
    self.assertFalse(User.objects.exists())
