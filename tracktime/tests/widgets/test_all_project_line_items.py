from djaveDT import to_tz_dt
from djaveTest.unit_test import get_test_user, TestCase

from tracktime.widgets.all_project_line_items import AllProjectLineItems
from tracktime.tests.models.test_project_line_item import (
    get_test_project_line_item)
from tracktime.tests.models.test_project_invoice import (
    get_test_project_invoice)


class AllProjectLineItemsTests(TestCase):
  def test_view(self):
    user = get_test_user()
    invoice = get_test_project_invoice(
        creator=user, created=to_tz_dt('2020-01-14'))
    get_test_project_line_item(invoice=invoice, hours=1)
    get_test_project_line_item(hours=1)
    all_line_items = AllProjectLineItems(
        user, {}, to_tz_dt('2020-01-15 12:00'))
    self.assertEqual(1, len(all_line_items.table.rows))
