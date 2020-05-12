from djaveForm.button import Button
from djaveForm.form import Form
from djaveForm.field import TextAreaField
from djaveTable.table import Table

from tracktime.models.to_do import ToDo


class ToDoForm(Form):
  def __init__(self):
    self.text_field = TextAreaField('text', required=True)
    self.save_button = Button('New to do', button_type='submit')
    super().__init__([self.text_field, self.save_button])


class ToDoTable(Table):
  def __init__(self, user, project, form_data):
    super().__init__()
    self.user = user
    self.project = project
    self.form_data = form_data

    self.setup_enter_new()
    self.setup_existing()

  def setup_enter_new(self):
    self.form = ToDoForm()
    if self.form_data:
      self.form.set_form_data(self.form_data)
      if self.form.save_button.get_was_clicked():
        if self.form.is_valid():
          ToDo.objects.create(
              user=self.user, project=self.project,
              description=self.form.text_field.get_value())
          self.form = ToDoForm()
    self.create_row([self.form.text_field, self.form.save_button])

  def setup_existing(self):
    for to_do in ToDo.objects.not_checked_off(self.user, self.project):
      done = Button('Done')
      delete = Button('Delete')
      self.create_row([to_do.description, [done, delete]], pk=to_do.pk)
