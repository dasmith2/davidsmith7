from djaveTest.unit_test import TestCase, get_test_user
from invoice.tests.models.test_line_item import get_test_line_item
from invoice.widgets.view_invoice import ViewInvoice


class ViewInvoiceTests(TestCase):
  def test_display(self):
    user = get_test_user()
    line_item = get_test_line_item(
        creator=user, describe_service='Dig pointlessly')
    view_invoice = ViewInvoice(line_item.invoice, None)
    html = view_invoice.as_html()
    self.assertTrue(html.find('Dig pointlessly') > 0)
    self.assertTrue(html.find(line_item.invoice.invoice_id) > 0)
