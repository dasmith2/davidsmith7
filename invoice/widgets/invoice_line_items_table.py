from djaveClass.edit_list_table import EditListTable
from djaveForm.button import Button
from djaveForm.field import TextAreaField, TextField, FloatField
from djaveTable.table import Table

from invoice.models.invoice_line_item import InvoiceLineItem


DESCRIBE_SERVICE = 'describe_service'
AMOUNT_CALCULATION = 'amount_calculation'
AMOUNT = 'amount'


class InvoiceLineItemsTable(EditListTable):
  def __init__(self, invoice):
    self.invoice = invoice

    super().__init__(
        InvoiceLineItem, ['Description', 'Calculation', 'Amount', ''])

    self.create_rows()
    self.wire_up_edit_ajax([DESCRIBE_SERVICE, AMOUNT_CALCULATION, AMOUNT])

  def create_rows(self):
    for line_item in self.invoice.invoicelineitem_set.order_by('pk'):
      describe = TextAreaField(
          DESCRIBE_SERVICE, default=line_item.describe_service)
      calculation = TextField(
          AMOUNT_CALCULATION, default=line_item.amount_calculation)
      amount = FloatField(AMOUNT, default=line_item.amount.amount)
      remove = Button('Remove')
      self.create_row([
          describe, calculation, amount, remove], pk=line_item.pk)
