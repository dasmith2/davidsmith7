from djaveTest.unit_test import TestCase
from djavError.widgets.too_many_queries_requests import TooManyQueriesRequests


class TooManyQueriesRequestsTests(TestCase):
  def test_display(self):
    TooManyQueriesRequests().as_html()
