""" This is really, like, UnpaidOrRecentlyPaidInvoicesTable. It doesn't have
many columns and it's trying to talk about invoices that are important right
now. """
from django.shortcuts import reverse
from django.template.loader import render_to_string
from djaveForm.button import Button
from djaveTable.table import Table
from djaveTable.cell_content import InHref


class InvoicesTable(Table):
  def __init__(self, user):
    self.user = user
    super().__init__(self.headers(), classes=['margin-top-half'])

    self._has_invoices = False
    self.add_invoice_rows()

    context = {
        'mark_invoice_paid_url': reverse('mark_invoice_paid'),
        'ajax_get_url': reverse('ajax_get')}
    self.js = render_to_string(
        'invoices_table.js',
        context=context)
    self.css = render_to_string('invoice_row_color.css')

  def get_invoices(self, nnow=None):
    return self.invoice_class().live.get_important_invoices(
        self.user, nnow=nnow)

  def add_invoice_rows(self):
    for invoice in self.get_invoices():
      self._has_invoices = True
      button_kwargs = {'pk': invoice.pk}

      edit_url = reverse(self.edit_invoice_view_name(), kwargs=button_kwargs)
      edit_button = InHref('Edit', edit_url, classes=['button', 'edit'])

      mark_paid_button = Button('Mark paid')

      view_text = 'Preview'
      if invoice.sent:
        view_text = 'View'

      view_url = reverse(self.view_invoice_view_name(), kwargs=button_kwargs)
      view_button = InHref(view_text, view_url, classes=['button view'])

      buttons = [view_button]
      if not invoice.paid:
        buttons.append(edit_button)
        if invoice.sent:
          buttons.append(mark_paid_button)

      row_class = invoice.status().lower()
      self.add_invoice_row(invoice, buttons, row_class)
