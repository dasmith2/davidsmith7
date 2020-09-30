""" This is really, like, UnpaidOrRecentlyPaidInvoicesTable. It doesn't have
many columns and it's trying to talk about invoices that are important right
now. """
from django.template.loader import render_to_string
from djaveCRUDTable.columns import (
    DisplayFieldColumn, DisplayMoneyColumn, ButtonsColumn,
    get_edit_button_for_column)
from djaveCRUDTable.crud_table import CRUDTable
from djaveCRUDTable.edit_table import FieldRow

from invoice.models.invoice import STATUS_TOOLTIP


class Invoices(CRUDTable):
  def __init__(self, user):
    self.user = user
    super().__init__(
        self.get_model(), self.get_display_columns(),
        visible_filters=self.get_filter_widgets(),
        edit_field_names_or_rows=self.get_edit_field_names_or_rows(),
        list_url=self.get_list_url(),
        label_edit_page_with_field='invoice_id',
        list_header=self.get_list_header(),
        margin_top_css=self.get_margin_top_css(), can_create_new=False,
        modified_row_callback='modified_invoice_row_callback',
        global_reload_function_name='reload_invoices',
        edit_callback='edit_invoice_callback',
        nav_css_class='project_invoices_nav')
    js_context = {
        'view_invoice_url_base': self.get_view_invoice_url_base()}
    self.add_js(render_to_string('js/invoices.js', context=js_context))

  def get_margin_top_css(self):
    return 'margin-top-half'

  def get_filter_widgets(self):
    return []

  def get_edit_field_names_or_rows(self):
    return [
        'sent_to',
        'make_payment_to',
        'service_from',
        'service_to',
        'sent',
        'net_days',
        FieldRow('due', widget=None, read_only=True)]

  def get_display_columns(self):
    return self.get_display_field_columns() + [
        ButtonsColumn([get_edit_button_for_column(self.get_list_url())])]

  def get_display_field_columns(self):
    return [
        DisplayFieldColumn('Invoice ID', 'invoice_id'),
        DisplayFieldColumn('Project', 'project_name'),
        DisplayMoneyColumn('Total', 'total'),
        DisplayFieldColumn(STATUS_TOOLTIP, 'status_with_date')]

  def get_list_header(self):
    raise NotImplementedError('get_list_header')

  def get_model(self):
    raise NotImplementedError('get_model')

  def get_list_url(self):
    raise NotImplementedError('get_list_url')

  def view_invoice_url_base(self):
    raise NotImplementedError('view_invoice_url_base')
