from djaveTest.unit_test import TestCase
from djavError.widgets.long_requests import LongRequests


class LongRequestsTests(TestCase):
  def test_display(self):
    LongRequests().as_html()
