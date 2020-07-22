from djaveTest.unit_test import TestCase, get_test_user
from tracktime.tests.models.test_project_invoice_rule import (
    get_test_project_invoice_rule)
from tracktime.widgets.project_invoice_rule_table import (
    ProjectInvoiceRuleTable)


class ProjectInvoiceRuleTableTests(TestCase):
  def test_render(self):
    creator = get_test_user()
    ProjectInvoiceRuleTable(creator, None, None).as_html()
    invoice_rule = get_test_project_invoice_rule(
        creator=creator, invoice_id_prefix='whatever')
    html = ProjectInvoiceRuleTable(
        creator, None, invoice_rule).as_html()
    self.assertTrue(html.find('whatever') > 0)
