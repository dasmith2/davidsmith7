from django.shortcuts import reverse
from djaveCRUDTable.columns import (
    DisplayFieldColumn, ButtonsColumn, get_edit_button_for_column)
from djaveCRUDTable.crud_table import CRUDTable
from djaveCRUDTable.edit_table import FieldRow
from djaveHTML.h import H2
from djaveHTML.tooltip import Tooltip

from tracktime.fields import project_field
from tracktime.models.project_invoice_rule import ProjectInvoiceRule


class RateColumn(DisplayFieldColumn):
  def template_template(self):
    return '$<%= {} %> / hr'


class ProjectInvoiceRules(CRUDTable):
  def __init__(self, user):
    self.user = user
    list_url = reverse('project_invoices')
    details_url_root = reverse('project_invoice_rules')
    buttons = [get_edit_button_for_column(details_url_root)]
    display_columns = [
        DisplayFieldColumn('Project', 'project_name'),
        RateColumn('Rate', 'hourly_rate'), ButtonsColumn(buttons)]
    project_row = FieldRow('project', widget=project_field(
        user=user, has_invoices=True), read_only=False)
    edit_field_names_or_rows = [
        project_row,
        'hourly_rate',
        'first_billable_day',
        'invoice_id_prefix',
        'sent_to',
        'make_payment_to',
        'default_line_item_description',
        'net_days']
    super().__init__(
        ProjectInvoiceRule, display_columns,
        list_url=list_url, details_url_root=details_url_root,
        save_new_defaults={'creator': 'me'},
        nav_css_class='invoices_nav',
        list_header=self.get_header(),
        margin_top_css='margin-top-half', new_button_text='Create new rule',
        modified_row_callback='new_project_invoice_rule_row_callback',
        edit_field_names_or_rows=edit_field_names_or_rows,
        edit_callback='edit_project_invoice_rule_callback')
    self.add_js_from_template(
        'js/project_invoice_rules.js',
        create_invoice_url=reverse('create_invoice'))

  def get_header(self):
    invoice_rule_help_text = (
        'An Invoice Rule has a "Create new invoice" button. When you click '
        'that button,')
    if self.rules_exist():
      invoice_rule_help_text = (
          'When you click the "Create new invoice" button,')
    invoice_rule_help_text += (
        ' it will find all un-invoiced work for that '
        'project and put it in an Invoice.')
    invoice_rules_header = Tooltip(
        'Invoice rules', invoice_rule_help_text, width=300)
    return H2(invoice_rules_header)

  def rules_exist(self):
    return ProjectInvoiceRule.filter_live(
        ProjectInvoiceRule.allowed_by_user(self.user)).exists()
