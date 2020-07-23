from djaveTest.unit_test import TestCase
from djavError.widgets.notifications_report import NotificationsReport
from djavError.tests.models.test_notification import get_test_notification


class NotificationsReportTests(TestCase):
  def test_display(self):
    get_test_notification(title='Stuff and stuff', count=1)
    self.assertTrue(
        NotificationsReport({}).as_html().find('Stuff and stuff') > 0)
