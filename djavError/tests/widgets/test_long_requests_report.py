from djaveTest.unit_test import TestCase
from djavError.tests.models.test_long_request import get_test_long_request
from djavError.widgets.long_requests_report import LongRequestsReport


class LongRequestsTests(TestCase):
  def test_display(self):
    get_test_long_request(total_duration=1234)
    long_requests_report = LongRequestsReport({})
    html = long_requests_report.as_html()
    self.assertTrue(html.find('1234') > 0)
