from djaveForm.button import Button
from djaveForm.field import TextAreaField, TextField, FloatField
from djaveTable.table import Table


class InvoiceLineItemsTable(Table):
  def __init__(self, request_data, invoice):
    self.request_data = request_data
    self.invoice = invoice

    super().__init__(['Description', 'Calculation', 'Amount', ''])
    self.create_rows()

  def create_rows(self):
    for line_item in self.invoice.invoicelineitem_set.all():
      describe = TextAreaField(
          'describe_service', default=line_item.describe_service)
      calculation = TextField(
          'amount_calculation', default=line_item.amount_calculation)
      amount = FloatField('amount', default=line_item.amount.amount)
      remove = Button('Remove')
      self.create_row([
          describe, calculation, amount, remove], pk=line_item.pk)
