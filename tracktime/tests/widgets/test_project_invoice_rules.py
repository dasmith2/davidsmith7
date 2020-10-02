from djaveTest.unit_test import TestCase, get_test_user
from tracktime.widgets.project_invoice_rules import ProjectInvoiceRules


class ProjectInvoiceRulesTests(TestCase):
  def test_display(self):
    ProjectInvoiceRules(get_test_user()).as_html()
