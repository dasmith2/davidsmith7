""" This is really, like, UnpaidOrRecentlyPaidInvoicesTable. It doesn't have
many columns and it's trying to talk about invoices that are important right
now. """
from django.shortcuts import reverse
from django.template.loader import render_to_string
from djaveClassMagic.edit_list_table import EditListTable
from djaveHTML.a import A

from invoice.models.invoice import Invoice


class InvoicesTable(EditListTable):
  def __init__(self, user):
    self.user = user
    super().__init__(Invoice, self.headers(), classes=['margin-top-half'])

    self._has_invoices = False
    self.add_invoice_rows()

    context = {'list_invoice_api_url': reverse(
        'list_or_save_new', kwargs={'model_name': 'Invoice'})}
    self.js = render_to_string('invoices_table.js', context=context)
    self.css = render_to_string('invoice_row_color.css')

  def headers(self):
    raise NotImplementedError('headers')

  def get_invoices(self, nnow=None):
    return self.invoice_class().live.get_important_invoices(
        self.user, nnow=nnow)

  def has_invoices(self):
    return self._has_invoices

  def add_invoice_rows(self):
    for invoice in self.get_invoices():
      self._has_invoices = True

      view_text = 'View' if invoice.sent else 'Preview'
      view_url = reverse(
          self.view_invoice_view_name(), kwargs={'pk': invoice.pk})
      view_button = A(view_text, view_url, classes=['button view'])

      row_class = invoice.status().lower()
      self.add_invoice_row(invoice, [view_button], row_class)
