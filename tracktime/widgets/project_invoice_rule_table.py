from djaveClass.edit_table import EditTable

from tracktime.fields import project_field
from tracktime.models.project_invoice_rule import ProjectInvoiceRule


class ProjectInvoiceRuleTable(EditTable):
  def __init__(self, user, request_POST, invoice_rule):
    self.user = user
    self.request_POST = request_POST
    self.invoice_rule = invoice_rule
    super().__init__(ProjectInvoiceRule, request_POST, invoice_rule)

  def add_rows(self):
    self.add_field_row('project', project_field(user=self.user))
    self.add_field_rows(
        'hourly_rate',
        'first_billable_day',
        'invoice_id_prefix',
        'make_payment_to',
        'email_to',
        'default_line_item_description',
        'net_days')
    self.add_final_row()

  def init_new(self):
    return ProjectInvoiceRule(creator=self.user)
