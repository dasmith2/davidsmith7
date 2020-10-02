from djaveTest.unit_test import TestCase
from djavError.widgets.errors import Errors


class ErrorsTests(TestCase):
  def test_display(self):
    Errors().as_html()
