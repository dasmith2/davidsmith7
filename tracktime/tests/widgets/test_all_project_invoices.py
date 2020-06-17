from djaveDT import to_tz_dt
from djaveTest.unit_test import get_test_user, TestCase

from tracktime.widgets.all_project_invoices import AllProjectInvoices
from tracktime.tests.models.test_project_invoice import (
    get_test_project_invoice)


class AllProjectInvoicesTests(TestCase):
  def test_view_all_project_invoices(self):
    user = get_test_user()
    get_test_project_invoice(
        creator=user, created=to_tz_dt('2020-01-14'))
    all_invoices = AllProjectInvoices(user, {}, to_tz_dt('2020-01-15 12:00'))
    self.assertEqual(1, len(all_invoices.table.rows))
