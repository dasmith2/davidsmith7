from django.shortcuts import reverse
from django.template.loader import render_to_string
from djaveClassMagic.edit_table import EditTable
from djaveForm.button import Button

from invoice.models.invoice import Invoice
from invoice.widgets.line_items_table import LineItemsTable


class EditInvoice(object):
  def __init__(self, request, request_POST, invoice):
    self.request = request
    self.invoice = invoice
    self.invoice_table = InvoiceTable(request_POST, invoice)
    self.line_items_table = LineItemsTable(request_POST, invoice)

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


class InvoiceTable(EditTable):
  def __init__(self, request_data, invoice):
    self.invoice = invoice
    save_and_preview_button = Button('Save and preview', button_type='submit')
    super().__init__(
        Invoice, request_data, instance=invoice,
        extra_buttons=[save_and_preview_button])

    self.redirect_to = None
    if save_and_preview_button.get_was_clicked(request_data):
      self.handle_save_click()
      if self.saved():
        self.redirect_to = reverse(
            'view_project_invoice', kwargs={'pk': invoice.pk})

  def add_rows(self):
    self.add_field_rows(
        'sent_to',
        'make_payment_to',
        'service_from',
        'service_to',
        'sent',
        'net_days')
    self.add_field_row('due', read_only=True)
    self.add_final_row()

  def handle_delete_click(self):
    for line_item in self.invoice.lineitem_set.all():
      line_item.as_child_class().mark_deleted()
    super().handle_delete_click()
