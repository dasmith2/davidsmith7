from djaveTest.unit_test import TestCase
from invoice.widgets.line_items import LineItems


class LineItemsTests(TestCase):
  def test_display(self):
    LineItems().as_html()
