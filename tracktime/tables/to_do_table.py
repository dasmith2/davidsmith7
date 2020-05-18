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
    self.save_button = Button('New to do', button_type='submit')
    fields = [self.description_field, self.save_button]
    if show_project:
      self.project_field = project_field(user)
      fields.append(self.project_field)
    super().__init__(fields)


class ToDoTable(Table):
  def __init__(self, user, project, form_data):
    """ If project is None, show a project column and pull to do items from all
    projects. """
    super().__init__()
    self.user = user
    self.project = project
    self.form_data = form_data

    self.setup_enter_new()
    self.setup_existing()

  def setup_enter_new(self):
    show_project = not bool(self.project)

    self.form = ToDoForm(self.user, show_project=show_project)
    if self.form.a_button_was_clicked(self.form_data):
      self.form.set_form_data(self.form_data)
      if self.form.save_button.get_was_clicked():
        if self.form.is_valid():
          project = self.project
          if not project:
            project = Project.live.get(
                pk=self.form.project_field.get_value())
            set_latest_project(self.user, project)
          ToDo.live.create(
              user=self.user, project=project,
              description=self.form.description_field.get_value())
          self.form = ToDoForm(self.user, show_project=show_project)

    cells = []
    if show_project:
      cells.append(self.form.project_field)
    cells.extend([self.form.description_field, self.form.save_button])
    self.create_row(cells)

  def setup_existing(self):
    for to_do in ToDo.live.not_done(self.user, self.project):
      done = Button('Done')
      # The save button is mainly here for usability. You save a to do
      # description by leaving the description text box which triggers a change
      # event. But if you change the description and then immediately click the
      # done button, there's a race between changing the description and
      # displaying the "Saved!" message, and between marking the thing done and
      # removing it from the list. So the whole point of this save button is to
      # give the user something to click on which will cause the cursor to
      # leave the text box.
      save = Button('Save')
      delete = Button('Delete')
      description = TextAreaField(
          'edit_description', default=to_do.description, required=False)

      cells = []
      if not bool(self.project):
        cells.append(to_do.project.name)
      cells.extend([description, [save, done, delete]])
      self.create_row(cells, pk=to_do.pk)
