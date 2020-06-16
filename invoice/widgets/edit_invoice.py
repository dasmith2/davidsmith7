from django.template.loader import render_to_string

from invoice.widgets.invoice_table import InvoiceTable
from invoice.widgets.line_items_table import LineItemsTable


class EditInvoice(object):
  def __init__(self, request, invoice):
    self.request = request
    self.invoice = invoice
    self.invoice_table = InvoiceTable(request.POST, invoice)
    self.line_items_table = LineItemsTable(request.POST, invoice)

  def redirect_to(self):
    return self.invoice_table.redirect_to

  def deleted(self):
    return self.invoice_table.deleted()

  def as_html(self):
    context = {
        'invoice': self.invoice,
        'invoice_table': self.invoice_table,
        'line_items_table': self.line_items_table}
    return render_to_string('edit_invoice.html', context, request=self.request)
