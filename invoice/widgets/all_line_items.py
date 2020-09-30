from djaveCRUDTable.columns import DisplayFieldColumn, DisplayMoneyColumn
from djaveCRUDTable.crud_table import CRUDTable

from invoice.models.invoice import STATUS_TOOLTIP
from invoice.models.line_item import LineItem


class AllLineItems(CRUDTable):
  def __init__(self, user):
    self.user = user
    super().__init__(
        LineItem, self.get_display_columns(),
        visible_filters=self.get_filters(), list_header='Line items',
        can_create_new=False, nav_css_class='project_invoices_nav',
        list_url=self.get_list_url(), list_api_url=self.get_list_api_url())

  def get_display_columns(self):
    status_column = DisplayFieldColumn(STATUS_TOOLTIP, 'invoice_status')
    return [
        DisplayFieldColumn('Invoice ID', 'invoice_id'),
        status_column,
        DisplayFieldColumn('Line item ID', 'id'),
        DisplayFieldColumn('Description', 'describe_service'),
        DisplayFieldColumn('Calculation', 'amount_calculation'),
        DisplayMoneyColumn('Amount', 'amount')]

  def get_filters(self):
    return []

  def get_list_url(self):
    raise NotImplementedError('get_list_url')

  def get_list_api_url(self):
    raise NotImplementedError('get_list_api_url')
