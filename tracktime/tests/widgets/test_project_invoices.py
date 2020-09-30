from tracktime.widgets.project_invoices import (
    ProjectInvoices, AllProjectInvoices)
from tracktime.tests.test_case_with_data import TestCaseWithData


class InvoicesTableTests(TestCaseWithData):
  def test_project_invoices(self):
    ProjectInvoices().as_html()

  def test_all_project_invoices(self):
    AllProjectInvoices().as_html()
