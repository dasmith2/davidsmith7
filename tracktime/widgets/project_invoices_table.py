from djaveTable.table import Cell

from invoice.widgets.invoices_table import InvoicesTable
from tracktime.models.project_invoice import ProjectInvoice


class ProjectInvoicesTable(InvoicesTable):
  def headers(self):
    return ['Invoice ID', 'Project', 'Total', 'Status', '']

  def has_invoices(self):
    return self._has_invoices

  def invoice_class(self):
    return ProjectInvoice

  def edit_invoice_view_name(self):
    return 'edit_project_invoice'

  def view_invoice_view_name(self):
    return 'view_invoice'

  def add_invoice_row(self, invoice, buttons, row_class):
    cells = [
        invoice.invoice_id, invoice.project.name, invoice.total,
        Cell(invoice.status_with_date(), classes=['status_cell']),
        Cell(buttons)]
    self.create_row(cells, classes=[row_class], pk=invoice.pk)
