from djaveTest.unit_test import TestCase, get_test_user
from invoice.tests.models.test_line_item import get_test_line_item
from invoice.widgets.all_line_items_table import AllLineItemsTable


class AllLineItemsTableTests(TestCase):
  def test_display(self):
    user = get_test_user()
    line_item = get_test_line_item(
        describe_service='Glue arms on', creator=user)
    all_line_items_table = AllLineItemsTable(user)
    all_line_items_table.add_rows([line_item])
    html = all_line_items_table.as_html()
    self.assertTrue(html.find('Glue arms on') > 0)
