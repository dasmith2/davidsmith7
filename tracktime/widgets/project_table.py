from djaveForm.button import Button
from djaveForm.field import TextField
from djaveForm.form import Form
from djaveTable.table import Table

from tracktime.models.project import Project


class BaseProjectTable(Table):
  def __init__(self):
    super().__init__(['Name', ''])

  def create_row_for_existing(self, project, archive_action):
    name_field = TextField('edit_name', default=project.name)
    archive_button = Button(archive_action)
    self.create_row([name_field, archive_button], pk=project.pk)


class ProjectTable(BaseProjectTable):
  def __init__(self, user, request_post):
    self.new_project_form = NewProjectForm()
    if request_post:
      self.new_project_form.set_form_data(request_post)
      if self.new_project_form.is_valid():
        self.new_project_form.save_new(creator=user)
        self.new_project_form = NewProjectForm()

    super().__init__()

    self.setup_create_new()
    self.setup_existing()

  def setup_create_new(self):
    self.create_row([
        self.new_project_form.name_field,
        self.new_project_form.save_new_button])

  def setup_existing(self):
    for project in Project.live.order_by('name'):
      self.create_row_for_existing(project, 'Archive')


class ArchivedProjectTable(BaseProjectTable):
  def __init__(self):
    super().__init__()
    self.setup_deleted()

  def setup_deleted(self):
    for project in Project.all.filter(deleted__isnull=False).order_by('name'):
      self.create_row_for_existing(project, 'Un-archive')


class NewProjectForm(Form):
  def __init__(self):
    self.name_field = NewProjectNameField()
    self.save_new_button = Button('Save new', button_type='submit')
    super().__init__([self.name_field, self.save_new_button])

  def save_new(self, creator):
    Project.live.create(name=self.name_field.get_value(), creator=creator)


class NewProjectNameField(TextField):
  def __init__(self):
    super().__init__('new_name', required=True)

  def explain_why_not_valid(self):
    reason = super().explain_why_not_valid()
    if reason:
      return reason
    if Project.all.filter(name=self.get_value()).exists():
      return 'A project with this name exists already'
