from django.contrib.auth.models import User
from djaveTest.unit_test import TestCase

from djaveClassMagic.get_test_instance import get_test_instance


class GetTestInstanceTests(TestCase):
  def test_get_test_user(self):
    user = get_test_instance(User, username='dave')
    self.assertEqual('dave', user.username)
