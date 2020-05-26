from djaveDT import now
from djaveForm.button import Button
from djaveForm.form import Form
from djaveForm.field import TextAreaField
from djaveTable.table import Table

from tracktime.fields import project_field
from tracktime.models.latest_project import set_latest_project
from tracktime.models.project import Project
from tracktime.models.to_do import ToDo


class ToDoForm(Form):
  def __init__(self, user, show_project):
    self.description_field = TextAreaField('new_description', required=True)
    self.to_do_button = Button('To do', button_type='submit')
    self.did_button = Button('Did', button_type='submit')
    fields = [self.description_field, self.to_do_button, self.did_button]
    if show_project:
      self.project_field = project_field(user)
      fields.append(self.project_field)
    super().__init__(fields)


class ToDoTable(Table):
  def __init__(self, user, project, form_data, nnow=None):
    """ If project is None, show a project column and pull to do items from all
    projects. """
    super().__init__()
    self.user = user
    self.project = project
    self.form_data = form_data

    self.setup_enter_new(nnow=nnow)
    self.setup_existing()

  def setup_enter_new(self, nnow=None):
    nnow = nnow or now()
    show_project = not bool(self.project)

    self.form = ToDoForm(self.user, show_project=show_project)
    if self.form.a_button_was_clicked(self.form_data):
      self.form.set_form_data(self.form_data)
      if self.form.is_valid():
        project = self.project
        if not project:
          project = Project.live.get(
              pk=self.form.project_field.get_value())
          set_latest_project(self.user, project)
        to_do = ToDo.live.create(
            creator=self.user, project=project,
            description=self.form.description_field.get_value())
        if self.form.did_button.get_was_clicked():
          to_do.done = nnow
          to_do.done_by = self.user
          to_do.save()
        self.form = ToDoForm(self.user, show_project=show_project)

    cells = []
    if show_project:
      cells.append(self.form.project_field)
    cells.extend([self.form.description_field, [
        self.form.to_do_button, self.form.did_button]])
    self.create_row(cells)

  def setup_existing(self):
    for to_do in ToDo.live.not_done(self.user, self.project):
      done = Button('Done')
      delete = Button('Delete')
      description = TextAreaField(
          'edit_description', default=to_do.description, required=False)

      cells = []
      if not bool(self.project):
        cells.append(to_do.project.name)
      cells.extend([description, [done, delete]])
      self.create_row(cells, pk=to_do.pk)
