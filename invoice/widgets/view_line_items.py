from django.utils.safestring import mark_safe
from djaveDT import d_to_str
from djaveTable.table import Table, Cell
from djmoney.money import Money

from invoice.html_email_context import html_context


class ViewLineItems(Table):
  def __init__(self, invoice):
    self.invoice = invoice
    self.line_items = list(invoice.lineitem_set.filter(
        deleted__isnull=True).order_by('pk'))
    self.any_calculations = self._compute_any_calculations(self.line_items)

    self.html_context = html_context()

    headers = ['Description', 'Amount']
    if self.any_calculations:
      headers = ['Description', 'Calculation', 'Amount']
    super().__init__(
        self.style_cells(headers, is_header=True),
        additional_attrs={'style': self.html_context['open_table_style']})

    self.add_line_item_rows()
    self.add_total_rows()

  def add_line_item_rows(self):
    for line_item in self.line_items:
      description = line_item.describe_service
      amount = line_item.amount
      calculation = line_item.amount_calculation

      row = [description, amount]
      if self.any_calculations:
        row = [description, calculation, amount]

      self.create_row(row)

  def add_total_rows(self):
    total_row = ['Total', self.invoice.total]
    if self.any_calculations:
      total_row = ['Total', None, self.invoice.total]

    self.create_row(total_row)

    if self.invoice.paid:
      paid_description = 'Paid on {}'.format(d_to_str(self.invoice.paid))
      paid_total = -self.invoice.total
      paid_row = [paid_description, paid_total]
      balance_row = ['Balance', Money(0, 'USD')]
      if self.any_calculations:
        paid_row = [paid_description, None, paid_total]
        balance_row = ['Balance', None, Money(0, 'USD')]
      self.create_row(paid_row)
      self.create_row(balance_row)

  def create_row(self, cells):
    super().create_row(self.style_cells(cells))

  def style_cells(self, cells, is_header=False):
    actual_row = []
    for cell in cells:
      additional_style = ''
      if isinstance(cell, str):
        cell = mark_safe(cell.replace('\n', '<br>\n'))
      if is_header:
        additional_style = ' background-color: #417690; color: #fff;'
      self.additional_cell_attrs = {
          'style': self.html_context['open_cell_style'] + additional_style}
      actual_row.append(Cell(
          cell, additional_attrs=self.additional_cell_attrs,
          is_header=is_header))
    return actual_row

  def _compute_any_calculations(self, line_items):
    for line_item in line_items:
      if line_item.amount_calculation:
        return True
    return False
