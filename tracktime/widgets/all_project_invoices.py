from datetime import timedelta

from django.template.loader import render_to_string
from djaveDT import now
from djaveForm.field import SelectField, Option
from djaveReport.date_range_report import DateRangeReport
from djaveTable.table import Table

from invoice.models.invoice import STATUSES
from tracktime.fields import project_field
from tracktime.models.project_invoice import ProjectInvoice


class AllProjectInvoicesTable(Table):
  def __init__(self, user):
    super().__init__([
        'Invoice_id', 'Project', 'Status', 'Total', 'Created', 'Sent', 'Due',
        'Paid'])
    self.user = user
    self.css = render_to_string('invoice_row_color.css')

  def add_rows(self, invoices):
    for invoice in invoices:
      self.create_row([
          invoice.invoice_id, invoice.project.name, invoice.status(),
          invoice.total, invoice.created, invoice.sent, invoice.due,
          invoice.paid], classes=[invoice.status().lower()])


class AllProjectInvoices(DateRangeReport):
  def __init__(self, user, request_get, nnow=None):
    nnow = nnow or now()
    today = nnow.date()
    default_from_date = today - timedelta(days=30)
    default_to_date = today
    project_filter = project_field(user=user, label='Project', required=False)
    status_filter = self.get_status_filter()
    filters = [project_filter, status_filter]

    self.all_invoices_table = AllProjectInvoicesTable(user)

    super().__init__(
        default_from_date, default_to_date, request_get=request_get,
        filters=filters, contents=self.all_invoices_table,
        from_filter_label='Created from')

    invoices = ProjectInvoice.live.get_invoices(
        user, self.from_date(), self.to_date(),
        project_filter.get_value_or_default(),
        status_filter.get_value_or_default())
    self.all_invoices_table.add_rows(invoices)

  def get_status_filter(self):
    return SelectField(
        key_prefix='status', options=self.status_options(), required=False,
        label='Status')

  def status_options(self):
    return [Option(option, option) for option in STATUSES]
