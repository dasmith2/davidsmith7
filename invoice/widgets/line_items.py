from django.shortcuts import reverse
from django.template.loader import render_to_string
from djaveCRUDTable.columns import EditFieldColumn, DeleteColumn
from djaveCRUDTable.crud_table import CRUDTable

from invoice.models.line_item import LineItem


class AmountCalculationColumn(EditFieldColumn):
  def __init__(self):
    super().__init__(LineItem, 'amount_calculation')

  def inline_create_cell(self):
    return '<td></td>'


class LineItems(CRUDTable):
  def __init__(self):
    display_columns = [
        EditFieldColumn(LineItem, 'describe_service'),
        AmountCalculationColumn(),
        EditFieldColumn(LineItem, 'amount'),
        DeleteColumn()]
    super().__init__(
        LineItem, display_columns, list_url='/invoices/:invoice_id',
        inline_create=True, list_header='Line items',
        global_reload_function_name='reload_line_items',
        list_api_url=reverse('list_or_save_new_line_item'),
        global_options_variable_name='line_items_options',
        saved_model_callback='saved_line_item_callback',
        deleted_model_callback='deleted_line_item_callback',
        modified_row_callback='new_line_item_row_callback')
    self.add_js(render_to_string('js/line_items.js'))
