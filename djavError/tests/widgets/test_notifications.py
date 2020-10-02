from djaveTest.unit_test import TestCase
from djavError.widgets.notifications import Notifications


class NotificationsTests(TestCase):
  def test_display(self):
    Notifications().as_html()
