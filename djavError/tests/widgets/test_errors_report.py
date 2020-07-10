from djavError.tests.models.test_error import get_test_error
from djavError.widgets.errors_report import ErrorsReport
from djaveTest.unit_test import TestCase


class ErrorsReportTests(TestCase):
  def test_table(self):
    get_test_error(title='The hogs have gone wild')
    self.assertTrue(
        ErrorsReport(None).as_html().find('The hogs have gone wild') >= 0)
