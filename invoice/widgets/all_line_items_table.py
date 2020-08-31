from django.template.loader import render_to_string
from djaveHTML.table import Table, Cell

from invoice.models.invoice import STATUS_TOOLTIP


class AllLineItemsTable(Table):
  def __init__(self, user):
    status = Cell(STATUS_TOOLTIP, is_header=True)
    super().__init__([
        'Invoice ID', status, 'Line item ID', 'Description',
        'Calculation', 'Amount'])
    self.user = user
    self.css = render_to_string('invoice_row_color.css')

  def add_rows(self, line_items):
    for li in line_items:
      self.create_row([
          li.invoice.invoice_id,  # Invoice ID
          li.invoice.status(),  # Status
          li.pk,
          li.describe_service,
          li.amount_calculation,
          li.amount], classes=[li.invoice.status().lower()])
