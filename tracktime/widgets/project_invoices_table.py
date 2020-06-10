from djaveTable.cell_content import InHref
from djaveTable.table import Table
from django.shortcuts import reverse

from tracktime.models.project_invoice import ProjectInvoice


class ProjectInvoicesTable(Table):
  def __init__(self, user):
    self.user = user
    super().__init__(
        ['Invoice ID', 'Project', 'Total', 'Created', 'Status'],
        classes=['margin-top-half'])

    self._has_invoices = False
    self.add_invoice_rows()

  def has_invoices(self):
    return self._has_invoices

  def add_invoice_rows(self):
    for invoice in ProjectInvoice.allowed_for_user_live(self.user):
      self._has_invoices = True
      url = reverse('project_invoice', kwargs={'pk': invoice.pk})
      invoice_id = InHref(invoice.invoice_id, url)
      self.create_row([
          invoice_id, invoice.project.name, invoice.total,
          invoice.created, invoice.status()])
