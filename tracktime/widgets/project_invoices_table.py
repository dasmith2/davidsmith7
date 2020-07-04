from django.shortcuts import reverse
from djaveTable.table import Cell

from invoice.widgets.invoices_table import InvoicesTable
from tracktime.models.project_invoice import ProjectInvoice


class ProjectInvoicesTable(InvoicesTable):
  def headers(self):
    return ['Invoice ID', 'Project', 'Total', 'Status', '']

  def invoice_class(self):
    return ProjectInvoice

  def view_invoice_view_name(self):
    return 'view_invoice'

  def add_invoice_row(self, invoice, buttons, row_class):
    cells = [
        invoice.invoice_id, invoice.project.name, invoice.total,
        Cell(invoice.status_with_date(), classes=['status_cell']),
        Cell(buttons, classes=['buttons'])]
    edit_url = reverse('edit_project_invoice', kwargs={'pk': invoice.pk})
    self.create_row(
        cells, classes=[row_class], pk=invoice.pk, additional_attrs={
            'data-paid': bool(invoice.paid), 'data-edit-url': edit_url,
            'data-class-if-not-paid': invoice.status_if_not_paid().lower()})
