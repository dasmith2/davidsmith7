from django.shortcuts import reverse

from djaveClassMagic.edit_list_table import EditListTable
from djaveHTML.button import Button
from djaveHTML.a import A

from tracktime.models.project_invoice_rule import ProjectInvoiceRule


class ProjectInvoiceRulesTable(EditListTable):
  def __init__(self, user, request_POST):
    self.user = user
    self.request_POST = request_POST
    super().__init__(
        ProjectInvoiceRule, ['Project', 'Rate', ''],
        classes=['margin-top-half'])
    self._has_rules = False
    self.add_rule_rows()
    self.create_new_button = self.append_create_new_row(
        'Create new rule', reverse('project_invoice_rule'))

  def has_rules(self):
    return self._has_rules

  def add_rule_rows(self):
    for rule in ProjectInvoiceRule.filter_live(
        ProjectInvoiceRule.allowed_by_user(self.user)):
      self._has_rules = True
      href = reverse('project_invoice_rule', kwargs={'pk': rule.pk})
      create_new_invoice_button = Button(
          'Create new invoice', button_type='submit', pk=rule.pk)
      if create_new_invoice_button.get_was_clicked(self.request_POST):
        rule.create_invoice()
      buttons = [A('Edit', href, button=True), create_new_invoice_button]
      self.create_row([
          rule.project.name, '{} / hr'.format(rule.hourly_rate),
          buttons], pk=rule.pk)
