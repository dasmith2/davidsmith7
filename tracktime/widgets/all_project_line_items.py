from django.shortcuts import reverse

from invoice.widgets.all_line_items import AllLineItems
from tracktime.widgets.project_invoices import get_filter_widgets


class AllProjectLineItems(AllLineItems):
  def get_filters(self):
    return get_filter_widgets(
        self.user, project_query_key='invoice__projectinvoice__project',
        created_query_key_prefix='invoice__created',
        status_query_key='invoice__status')

  def get_list_url(self):
    return reverse('project_line_items')

  def get_list_api_url(self):
    return reverse('list_or_save_new_line_item')
