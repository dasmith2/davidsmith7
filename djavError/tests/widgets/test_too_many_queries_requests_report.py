from djaveTest.unit_test import TestCase
from djavError.tests.models.test_too_many_queries_request import (
    get_test_too_many_queries_request)
from djavError.widgets.too_many_queries_requests_report import (
    TooManyQueriesRequestsReport)


class TooManyQueriesRequestsTests(TestCase):
  def test_display(self):
    get_test_too_many_queries_request(total_query_count=30)
    too_many_queries_requests = TooManyQueriesRequestsReport({})
    html = too_many_queries_requests.as_html()
    self.assertTrue(html.find('30') > 0)
