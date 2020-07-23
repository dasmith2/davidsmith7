from djaveTest.unit_test import TestCase
from invoice.tests.models.test_line_item import get_test_line_item
from invoice.widgets.line_items_table import LineItemsTable


class LineItemsTableTests(TestCase):
  def test_display(self):
    line_item = get_test_line_item(describe_service='Dig pointlessly')
    line_items_table = LineItemsTable({}, line_item.invoice)
    html = line_items_table.as_html()
    self.assertTrue(html.find('Dig pointlessly') > 0)
