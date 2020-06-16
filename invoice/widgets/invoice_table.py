from django.shortcuts import reverse
from djaveClass.edit_table import EditTable
from djaveForm.button import Button

from invoice.models.invoice import Invoice


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
        'service_to')
    if self.invoice.due:
      self.add_field_row('due')
    else:
      self.add_field_row('net_days')
    self.add_final_row()

  def handle_delete_click(self):
    for line_item in self.invoice.lineitem_set.all():
      line_item.as_child_class().mark_deleted()
    super().handle_delete_click()
