from tracktime.widgets.project_invoices_table import ProjectInvoicesTable
from tracktime.tests.test_case_with_data import TestCaseWithData
from tracktime.tests.models.test_project_invoice import (
    get_test_project_invoice)


class InvoicesTableTests(TestCaseWithData):
  def test_view(self):
    self.setup_user()
    self.setup_projects()

    get_test_project_invoice(creator=self.user, project=self.project_1)
    table = ProjectInvoicesTable(self.user)
    self.assertEqual(1, len(table.rows))
