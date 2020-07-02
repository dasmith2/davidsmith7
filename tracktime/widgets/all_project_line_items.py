from invoice.models.line_item import LineItem
from invoice.widgets.all_line_items_table import AllLineItemsTable
from tracktime.widgets.all_project_invoices import AllProjectInvoices


class AllProjectLineItems(AllProjectInvoices):
  def get_table(self):
    return AllLineItemsTable(self.user)

  def get_line_items(self):
    return LineItem.live.get_line_items_from_invoices(
        self.get_invoices())

  def add_rows(self):
    self.table.add_rows(self.get_line_items())
