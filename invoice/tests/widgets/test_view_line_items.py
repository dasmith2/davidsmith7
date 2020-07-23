from djaveTest.unit_test import TestCase, get_test_user
from invoice.tests.models.test_line_item import get_test_line_item
from invoice.widgets.view_line_items import ViewLineItems


class ViewLineItemsTests(TestCase):
  def test_display(self):
    user = get_test_user()
    line_item = get_test_line_item(
        creator=user, describe_service='Dig pointlessly')
    view_line_items = ViewLineItems(line_item.invoice)
    html = view_line_items.as_html()
    self.assertTrue(html.find('Dig pointlessly') > 0)
