from djaveAPI.to_json import to_json_dict
from djaveTest.unit_test import TestCase
from invoice.tests.models.test_invoice import get_test_invoice
from invoice.widgets.edit_invoice import EditInvoice


class EditInvoiceTests(TestCase):
  def test_save(self):
    invoice = get_test_invoice(sent_to='Dave Street')
    invoice_table = EditInvoice(None, {}, invoice)
    html = invoice_table.as_html()
    self.assertTrue(html.find('Dave Street') > 0)

    data = to_json_dict(invoice)
    data['sent_to'] = 'Steve Street'
    data['save'] = 'yep'
    EditInvoice(None, data, invoice)
    invoice.refresh_from_db()
    self.assertEqual('Steve Street', invoice.sent_to)
