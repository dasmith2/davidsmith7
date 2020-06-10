from django.template.loader import render_to_string

from invoice.widgets.invoice_table import InvoiceTable
from invoice.widgets.invoice_line_items_table import InvoiceLineItemsTable


class EditInvoice(object):
  def __init__(self, request, invoice):
    self.request = request
    self.invoice = invoice
    self.invoice_table = InvoiceTable(request.POST, invoice)
    self.invoice_line_items_table = InvoiceLineItemsTable(
        request.POST, invoice)

  def deleted(self):
    return self.invoice_table.deleted()

  def as_html(self):
    context = {
        'invoice': self.invoice,
        'invoice_table': self.invoice_table,
        'invoice_line_items_table': self.invoice_line_items_table}
    return render_to_string('edit_invoice.html', context, request=self.request)
