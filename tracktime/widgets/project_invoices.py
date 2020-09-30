from datetime import date

from django.shortcuts import reverse
from djaveCRUDTable.columns import DisplayFieldColumn, DisplayMoneyColumn
from djaveCRUDTable.filters import from_filter, to_filter
from djaveDT import add_months
from djaveHTML.tooltip import Tooltip
from djaveHTML.h import H2

from invoice.fields import status_field
from invoice.models.invoice import STATUS_TOOLTIP
from invoice.widgets.invoices import Invoices
from tracktime.fields import project_field
from tracktime.models.project_invoice import ProjectInvoice


def get_filter_widgets(
    user, project_query_key=None, created_query_key_prefix=None,
    status_query_key=None):
  project = project_field(
      user, label='Project', required=False, has_invoices=True,
      query_key=project_query_key)
  use_created_query_key_prefix = created_query_key_prefix or 'created'
  from_f = from_filter(
      use_created_query_key_prefix,
      default=add_months(date.today(), -1), label='Created from')
  to_f = to_filter(use_created_query_key_prefix)
  return [from_f, to_f, project, status_field(status_query_key)]


class ProjectInvoices(Invoices):
  def get_model(self):
    return ProjectInvoice

  def get_list_url(self):
    return reverse('project_invoices')

  def get_view_invoice_url_base(self):
    return reverse(
        'view_project_invoice', kwargs={'pk': '1'}).replace('/1', '/')

  def get_list_header(self):
    unpaid_help_text = 'Well, technically, unpaid and recently paid.'
    return H2([Tooltip('Unpaid', unpaid_help_text), ' invoices'])


class AllProjectInvoices(ProjectInvoices):
  def get_filter_widgets(self):
    return get_filter_widgets(self.user)

  def get_list_url(self):
    return reverse('all_project_invoices')

  def get_display_columns(self):
    return [
        DisplayFieldColumn('Invoice ID', 'invoice_id'),
        DisplayFieldColumn('Project', 'project_name'),
        DisplayMoneyColumn('Total', 'total'),
        DisplayFieldColumn(STATUS_TOOLTIP, 'status'),
        DisplayFieldColumn('Created', 'created_str'),
        DisplayFieldColumn('Sent', 'sent_str'),
        DisplayFieldColumn('Due', 'due_str'),
        DisplayFieldColumn('Paid', 'paid_str')]

  def get_list_header(self):
    return None

  def get_margin_top_css(self):
    return 'margin-top'
