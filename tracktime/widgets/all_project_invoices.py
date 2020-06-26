from datetime import timedelta

from django.shortcuts import reverse
from django.template.loader import render_to_string
from djaveDT import now
from djaveForm.field import SelectField, Option
from djaveReport.date_range_report import DateRangeReport
from djaveTable.cell_content import InHref
from djaveTable.table import Table

from invoice.models.invoice import STATUSES
from tracktime.fields import project_field
from tracktime.models.project_invoice import ProjectInvoice


class AllProjectInvoicesTable(Table):
  def __init__(self, user):
    see_line_items_button = InHref(
        'See all line items', reverse('project_line_items'),
        classes=['all_line_items'])
    super().__init__([
        'Invoice ID', 'Project', 'Status', 'Total', 'Created', 'Sent', 'Due',
        'Paid'], post_table_buttons=[see_line_items_button])
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
    self.user = user

    nnow = nnow or now()
    today = nnow.date()
    default_from_date = today - timedelta(days=30)
    default_to_date = today
    self.project_filter = project_field(
        user=user, label='Project', required=False)
    self.status_filter = self.get_status_filter()
    filters = [self.project_filter, self.status_filter]

    self.table = self.get_table()

    super().__init__(
        default_from_date, default_to_date, request_get=request_get,
        filters=filters, contents=self.table, from_filter_label='Created from')

    self.add_rows()

  def get_table(self):
    return AllProjectInvoicesTable(self.user)

  def get_invoices(self):
    return ProjectInvoice.live.get_invoices(
        self.user, self.from_date(), self.to_date(),
        self.project_filter.get_value_or_default(),
        self.status_filter.get_value_or_default())

  def add_rows(self):
    self.table.add_rows(self.get_invoices())

  def get_status_filter(self):
    return SelectField(
        key_prefix='status', options=self.status_options(), required=False,
        label='Status')

  def status_options(self):
    return [Option(option, option) for option in STATUSES]
