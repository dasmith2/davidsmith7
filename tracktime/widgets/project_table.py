from django.db.models import Q
from djaveClassMagic.edit_table import EditTable
from djaveForm.field import TextField

from tracktime.models.project import Project


class ProjectTable(EditTable):
  def __init__(self, user, request_POST, project):
    self.user = user
    super().__init__(Project, request_POST, project, show_delete=False)

  def add_rows(self):
    self.add_field_row('name', NewProjectNameField(self.instance))
    self.add_field_rows('use_clock', 'has_to_do_list', 'has_invoices')
    self.add_final_row()

  def init_new(self):
    return Project(creator=self.user)


class NewProjectNameField(TextField):
  def __init__(self, instance):
    self.instance = instance
    super().__init__('name', required=True)

  def explain_why_not_valid(self):
    reason = super().explain_why_not_valid()
    if reason:
      return reason
    finder = Project.objects.filter(name=self.get_value())
    if self.instance and self.instance.pk:
      finder = finder.filter(~Q(pk=self.instance.pk))
    if finder.exists():
      return 'A project with this name exists already'
