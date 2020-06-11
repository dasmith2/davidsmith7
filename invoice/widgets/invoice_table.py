from djaveClass.edit_table import EditTable

from invoice.models.invoice import Invoice


class InvoiceTable(EditTable):
  def __init__(self, request_data, invoice):
    self.invoice = invoice
    super().__init__(Invoice, request_data, instance=invoice)

  def add_rows(self):
    self.add_field_rows(
        'make_payment_to',
        'email_to',
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
