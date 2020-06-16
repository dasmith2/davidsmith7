from djmoney.money import Money
from tracktime.tests.test_case_with_data import TestCaseWithData
from tracktime.tests.models.test_project_invoice_rule import (
    get_test_project_invoice_rule)
from tracktime.widgets.project_invoice_rules_table import (
    ProjectInvoiceRulesTable)


class ProjectInvoiceRulesTableTests(TestCaseWithData):
  def test_view(self):
    self.setup_user()
    self.setup_projects()

    get_test_project_invoice_rule(
        creator=self.user, project=self.project_1,
        hourly_rate=Money(90, 'USD'))

    self.assertEqual(2, len(ProjectInvoiceRulesTable(self.user, {}).rows))
