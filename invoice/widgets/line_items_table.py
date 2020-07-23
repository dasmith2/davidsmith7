from djaveClassMagic.edit_list_table import EditListTable
from djaveForm.button import Button
from djaveForm.field import TextAreaField, TextField, MoneyField
from djaveForm.form import Form
from djmoney.money import Money

from invoice.models.line_item import LineItem
from invoice.models.manual_line_item import ManualLineItem


DESCRIBE_SERVICE = 'describe_service'
AMOUNT_CALCULATION = 'amount_calculation'
AMOUNT = 'amount'


class LineItemForm(Form):
  def __init__(self, invoice):
    self.invoice = invoice
    self.description = TextAreaField('new_description')
    self.amount = MoneyField('new_amount')
    self.save_button = Button('New manual Line Item', button_type='submit')
    super().__init__([self.description, self.amount, self.save_button])

  def save(self):
    money_amount = self.amount.get_value()
    ManualLineItem.live.create(
        invoice=self.invoice, describe_service=self.description.get_value(),
        amount=Money(money_amount, 'USD'), amount_calculation='')


class LineItemsTable(EditListTable):
  def __init__(self, request_POST, invoice):
    self.invoice = invoice
    self.form = LineItemForm(invoice)
    if self.form.save_button.get_was_clicked(request_POST):
      self.form.set_form_data(request_POST)
      if self.form.is_valid():
        self.form.save()
        self.form = LineItemForm(invoice)

    super().__init__(
        LineItem, ['Description', 'Calculation', 'Amount', ''],
        classes=['margin-top-half'])

    self.create_top_row()
    self.create_line_item_rows()
    self.setup_edit_ajax([DESCRIBE_SERVICE, AMOUNT_CALCULATION, AMOUNT])
    self.setup_delete_ajax(
        '.remove', 'Remove?\n\n(This will show up\nin the next invoice)')
    self.setup_delete_ajax(
        '.delete_line_item', 'Delete?\n\n(This will go away forever)')

  def create_top_row(self):
    self.create_row([
        self.form.description, None, self.form.amount, self.form.save_button])

  def create_line_item_rows(self):
    for line_item in self.invoice.lineitem_set.filter(
        deleted__isnull=True).order_by('pk'):
      is_manual = line_item.child_class.model_class() is ManualLineItem

      describe = TextAreaField(
          DESCRIBE_SERVICE, default=line_item.describe_service)
      calculation = TextField(
          AMOUNT_CALCULATION, default=line_item.amount_calculation)
      amount = MoneyField(AMOUNT, default=line_item.amount.amount)
      button = Button('Remove')
      if is_manual:
        button = Button('Delete', key_prefix='delete_line_item')
        calculation = None
      self.create_row([
          describe, calculation, amount, button], pk=line_item.pk)
