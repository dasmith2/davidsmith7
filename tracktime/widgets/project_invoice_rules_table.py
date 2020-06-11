from django.shortcuts import reverse

from djaveForm.button import Button
from djaveTable.cell_content import InHref
from djaveTable.table import Table, Cell

from tracktime.models.project_invoice_rule import ProjectInvoiceRule


class ProjectInvoiceRulesTable(Table):
  def __init__(self, user, request_POST):
    self.user = user
    self.request_POST = request_POST
    super().__init__(['Project', 'Rate', ''], classes=['margin-top-half'])
    self._has_rules = False
    self.add_rule_rows()
    self.add_final_row()

  def has_rules(self):
    return self._has_rules

  def add_rule_rows(self):
    for rule in ProjectInvoiceRule.allowed_by_user_live(self.user):
      self._has_rules = True
      href = reverse('project_invoice_rule', kwargs={'pk': rule.pk})
      create_new_invoice_button = Button(
          'Create new invoice', button_type='submit', pk=rule.pk)
      if create_new_invoice_button.get_was_clicked(self.request_POST):
        rule.create_invoice()
      self.create_row([
          InHref(rule.project.name, href), rule.hourly_rate,
          create_new_invoice_button])

  def add_final_row(self):
    self.create_new_button = InHref(
        'Create new rule', reverse('project_invoice_rule'), classes=['button'])
    create_new_cell = Cell(
        self.create_new_button,
        additional_attrs={'colspan': len(self.headers)}, classes=['pad-half'])
    self.create_row([create_new_cell])
