from djaveTable.table import Table

from tracktime.models.project_line_item import ProjectLineItem
from tracktime.widgets.all_project_invoices import AllProjectInvoices
from django.template.loader import render_to_string


class AllProjectLineItemsTable(Table):
  def __init__(self, user):
    super().__init__([
        'Invoice ID', 'Project', 'Status', 'Line item ID', 'Description',
        'Calculation', 'Amount'])
    self.user = user
    self.css = render_to_string('invoice_row_color.css')

  def add_rows(self, line_items):
    for li in line_items:
      self.create_row([
          li.invoice.invoice_id,  # Invoice ID
          li.invoice.projectinvoice.project.name,  # Project
          li.invoice.status(),  # Status
          li.pk,
          li.describe_service,
          li.amount_calculation,
          li.amount], classes=[li.invoice.status().lower()])


class AllProjectLineItems(AllProjectInvoices):
  def get_table(self):
    return AllProjectLineItemsTable(self.user)

  def get_line_items(self):
    return ProjectLineItem.live.get_line_items_from_invoices(
        self.get_invoices())

  def add_rows(self):
    self.table.add_rows(self.get_line_items())
